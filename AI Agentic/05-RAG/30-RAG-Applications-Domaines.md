# Étape 30 — RAG — Applications du RAG par domaine

> Étape 30 du parcours · Prérequis : [Exemples de RAG de bout en bout](<29-RAG-Exemples-Cas-Usage.md>) · Suite : [Reranking par cross-encodeur](<30b-RAG-Reranking-Cross-Encodeur.md>)

**Dossier :** 05-RAG  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  
**Nom du fichier :** 30-RAG-Applications-Domaines.md

## Ce que contient ce fichier

L'étape 29 faisait tourner une question par domaine pour montrer la chaîne RAG de bout en bout. Ce fichier prend le point de vue de l'équipe qui exploite ces agents en production : pour chacun des sept acteurs du parcours, comment les documents sont découpés, quelle fonction classe les morceaux, quelle métrique juge le résultat, et quel seuil transforme cette mesure en décision. Un tableau de bord en Python rejoue ensuite une campagne d'évaluation avant mise en production : chaque proportion reçoit son intervalle de Wilson à 95 %, et un domaine n'est déployé que si toutes ses barrières passent. Les comptes de la campagne (190 questions réussies sur 200, etc.) sont inventés pour l'exemple : ils servent à montrer le raisonnement, pas à décrire un système réel. Seuls les chiffres réglementaires cités reprennent la liste vérifiée du parcours.

## Ce que corrige ce fichier

L'ancien tableau avait une seule colonne « Métriques clés » qui mélangeait trois natures d'objets. Il y rangeait des **fonctions de score** (« Cosine », « Hybrid score », « BM25 + cosine »), qui classent les morceaux à chaque requête et ne mesurent rien ; des **métriques d'évaluation** (« Faithfulness », « Recall@k », « NDCG », « MRR »), qui jugent un classement ou une réponse sur un jeu de questions annotées ; et un **garde-fou** (« Guardrails + Faithfulness »), qui décide en ligne de bloquer ou non une réponse. Il citait aussi le « Recall » sans préciser k, et l'Answer Relevancy sans la définir (elle l'est à l'étape 55). Le nouveau tableau sépare quatre colonnes : le découpage (comment on coupe), la fonction de score (comment on classe), la métrique d'évaluation (comment on juge) et le seuil de décision (comment on tranche).

## Tableau par domaine

Les seuils sont illustratifs : chaque équipe les fixe selon le coût d'une erreur dans son métier.

| Domaine | Usage du RAG | Découpage (chunking) | Fonction de score | Métrique d'évaluation | Seuil de décision |
|---|---|---|---|---|---|
| Banque | réponses sur la politique de crédit et les règles de la CBUAE | un article de politique ou de règlement par morceau, avec le titre de la section répété | BM25 et cosinus fusionnés par RRF, puis reranker | HitRate@5 ; part de réponses fidèles (étape 54) | borne basse de Wilson d'au moins 0,90 pour chacune |
| Immobilier | estimation à partir de transactions comparables | une transaction par morceau (fiche structurée : quartier, type, surface, date, prix) | filtre par quartier et type, puis cosinus | part d'estimations fiables ; NDCG@5 sur des notes de 0 à 3 (étape 28) | borne basse d'au moins 0,80 ; sinon estimation annoncée comme peu fiable |
| Crypto | procédures internes et grilles de frais d'une plateforme agréée VARA | une section par morceau, avec son identifiant de version | BM25 et cosinus fusionnés par RRF, filtre « en vigueur » | HitRate@3 ; part de réponses citant une version remplacée ; MRR@3 (étape 27) | borne basse d'au moins 0,85 ; borne haute d'au plus 0,03 pour les versions remplacées |
| Assurance | clauses du contrat de l'assuré pour instruire un sinistre | une clause par morceau (garantie, exclusion, franchise) | cosinus et reranker, filtre par version du contrat | part de réponses fidèles ; NDCG@5 | borne basse d'au moins 0,85 ; en ligne, revue humaine dès qu'une phrase n'est pas étayée |
| RH | règles de fin de service, de visa et de paie selon le régime du salarié | une règle par morceau, régime juridique en métadonnée | filtre par régime, puis BM25 et cosinus | HitRate@3 ; part de réponses données sans régime connu ; Precision@4 (étape 26) | borne basse d'au moins 0,85 ; borne haute d'au plus 0,03 pour les réponses sans régime |
| BTP | clauses des contrats de sous-traitance pour contrôler les factures | une clause de contrat par morceau, identifiant du lot en métadonnée | BM25 et cosinus fusionnés par RRF, filtre par lot | part de questions avec le bon contrat au rang 1 (Success@1, égal au MRR@1) | borne basse d'au moins 0,75 ; en ligne, revue humaine si aucune clause spécifique n'est dans le top-3 |
| Secteur public | pages de démarches en arabe et en anglais | une page de démarche par morceau et par langue | BM25 sur texte normalisé (arabe) et cosinus multilingue | HitRate@3 par langue ; part d'abstentions correctes hors périmètre | borne basse d'au moins 0,80 dans chaque langue ; en ligne, abstention si le meilleur cosinus est sous le seuil calibré |

## Démonstration

### 1. Une proportion observée au-dessus du seuil ne suffit pas

Pour une barrière, on compte s succès sur n questions, et l'on estime la proportion par p̂ = s / n. L'intervalle de Wilson à 95 %, démontré à l'étape 7 et recopié ici depuis le code canonique, vaut :

$$
\hat{p} = \frac{s}{n}
$$

$$
\text{IC}_{95\,\%} = \frac{\hat{p} + \dfrac{z^2}{2n} \pm z\sqrt{\dfrac{\hat{p}(1-\hat{p})}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}} \qquad \text{avec} \qquad z = 1{,}96
$$

Une barrière « minimum » passe si la **borne basse** atteint le seuil ; une barrière « maximum » passe si la **borne haute** reste dessous. On exige la borne et non la valeur observée parce qu'un jeu de 200 questions n'est qu'un échantillon : la borne basse est la plus petite proportion compatible avec ce qu'on a observé, au niveau de confiance choisi.

Cas de la banque : 183 réponses fidèles sur 200, soit p̂ = 0,915, au-dessus du seuil de 0,90. Avec z² = 3,8416, le dénominateur vaut 1 + 3,8416 / 200 = 1,019208, le centre (0,915 + 0,009604) / 1,019208 ≈ 0,9072 et la demi-largeur ≈ 0,0391. La borne basse vaut donc ≈ 0,8681, sous 0,90 : la barrière échoue et le domaine est bloqué, alors que la proportion observée dépasse le seuil. Pour savoir combien de questions il faudrait pour une marge de ± 0,02 autour de 0,90, on applique la formule de taille d'échantillon de l'étape 7 :

$$
n = \frac{z^2\, p\,(1-p)}{e^2} = \frac{3{,}8416 \times 0{,}9 \times 0{,}1}{0{,}02^2} = 864{,}36
$$

soit 865 questions, plus de quatre fois le jeu actuel.

### 2. Zéro échec observé ne veut pas dire zéro risque

Les barrières « au plus 3 % » des domaines crypto et RH portent sur des événements qui ne se sont jamais produits pendant la campagne : 0 réponse sur 150 a cité une version remplacée. Avec s = 0, on a p̂ = 0, et la formule de Wilson se simplifie, parce que le terme p̂(1 − p̂)/n disparaît et que la racine de z²/(4n²) vaut z/(2n) :

$$
\text{centre} = \frac{z^2/(2n)}{1 + z^2/n} = \frac{z^2}{2(n + z^2)} \qquad \text{demi-largeur} = \frac{z \cdot z/(2n)}{1 + z^2/n} = \frac{z^2}{2(n + z^2)}
$$

Le centre et la demi-largeur sont égaux, donc la borne basse vaut exactement 0 et la borne haute vaut leur somme :

$$
\text{borne haute}(0, n) = \frac{z^2}{n + z^2}
$$

Pour n = 150, elle vaut 3,8416 / 153,8416 ≈ 0,0250 : avec 95 % de confiance, le taux réel d'erreur est d'au plus 2,5 %, sous le seuil de 3 %, et la barrière passe. Pour qu'une campagne sans échec franchisse ce seuil, il faut z² / (n + z²) ≤ 0,03, c'est-à-dire n ≥ z² (1/0,03 − 1) ≈ 124,21 : au moins 125 questions sans aucun échec.

L'intervalle « normal » naïf, p̂ ± z√(p̂(1 − p̂)/n), dit de Wald, montre pourquoi on ne l'utilise pas ici :

$$
\text{IC}_{Wald} = \hat{p} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n}}
$$

Avec 0 succès sur 150, sa largeur est nulle : il annonce [0 ; 0], une certitude absurde après seulement 150 essais. Avec 47 succès sur 50, sa borne haute vaut 1,0058, au-dessus de 1, ce qui est impossible pour une proportion. Wilson donne respectivement [0 ; 0,0250] et une borne haute de 0,9794.

### 3. Les moyennes ne reçoivent pas d'intervalle de Wilson

Le MRR@3, le NDCG@5 ou la Precision@4 sont des moyennes de valeurs comprises entre 0 et 1 (un rang réciproque de 0,5, un NDCG de 0,934), pas des comptes de succès. L'intervalle de Wilson suppose au contraire que chaque question est un essai à deux issues, réussi ou raté, indépendant des autres. Le tableau de bord affiche donc ces moyennes à part, sans intervalle, et fonde ses barrières sur des proportions qu'on peut compter : le HitRate@k (part des questions dont le rang réciproque est positif) ou le Success@1 (part des questions dont le premier résultat est pertinent, égal au MRR@1, étape 27). C'est pourquoi la barrière du BTP porte sur « le bon contrat au rang 1 » plutôt que sur le MRR@3. Pour encadrer une moyenne, on rééchantillonne les questions (bootstrap), ce qui sort du cadre de ce fichier.

### 4. Une proportion mesurée sur trop peu de cas ne juge rien

L'assureur suit aussi la part des revues humaines qui confirment une vraie erreur, c'est-à-dire la précision de son garde-fou de fidélité. Elle vaut 22 sur 29, soit 0,759, mais son intervalle de Wilson va de 0,5789 à 0,8778 : une largeur de presque 0,30. Avec 29 cas, on ne peut ni affirmer que le garde-fou est bon, ni qu'il est mauvais. Cet indicateur reste donc un suivi, pas une barrière, tant que le nombre de revues n'a pas atteint quelques centaines.

## Le programme

### Déroulé, ligne par ligne

**`wilson(succes, n, z)`** est la fonction canonique du parcours, recopiée telle quelle. Elle renvoie `None` quand `n` vaut 0, faute de dénominateur, et lève `ValueError` si `succes` sort de l'intervalle de 0 à `n`. Pour `wilson(183, 200)`, `p` vaut 0.915, `d` vaut 1.019208, `centre` 0.9072 et `demi` 0.0391, d'où l'intervalle (0.8681, 0.9463).

**`wald(succes, n, z)`** calcule l'intervalle naïf **sans** le ramener dans [0, 1], exprès, pour montrer qu'il en sort : `wald(47, 50)` a une borne haute de 1.0058.

**`taille_echantillon(p, marge, z)`** applique la formule de l'étape 7 et arrondit au-dessus avec `math.ceil` : on ne fait pas une demi-question. `taille_echantillon(0.90, 0.02)` vaut 865.

**`Barriere`** décrit une proportion mesurée (`succes` sur `n`) et son exigence (`seuil` et `sens`).

- `intervalle()` appelle `wilson` et lève `ValueError` si `n` vaut 0 : une barrière sans aucune question ne peut pas passer par défaut.
- `passe()` compare la borne basse au seuil si `sens` vaut `"min"`, la borne haute si `sens` vaut `"max"`. Pour les réponses fidèles de la banque, `0.8681 >= 0.90` est faux : la barrière échoue.

**`Domaine`** regroupe le nom, la fonction de score, le découpage, la liste des barrières et le dictionnaire des moyennes. `decision()` renvoie `"déployer"` seulement si **toutes** les barrières passent, grâce à `all(...)` : une seule barrière qui échoue bloque le domaine.

**`tableau_de_bord()`** construit les sept domaines avec les comptes illustratifs de la campagne.

**`main()`**, bloc par bloc.

1. Une ligne par barrière : le domaine, le nom, la proportion observée, l'intervalle de Wilson, l'exigence et le résultat. La liste `attendus` vérifie les douze intervalles à quatre décimales et les douze résultats.
2. Les décisions des sept domaines sont affichées et vérifiées. On vérifie aussi le paradoxe apparent de la banque (0,915 au-dessus de 0,90, et pourtant bloquée), avec le dénominateur, le centre et la demi-largeur du point 1 de la démonstration.
3. Les moyennes sont affichées à part, sans intervalle (point 3).
4. Le suivi de l'assureur, 22 sur 29, montre un intervalle large de plus de 0,29 (point 4).
5. Le contre-exemple de Wald : largeur nulle pour 0 sur 150, borne haute au-dessus de 1 pour 47 sur 50. On vérifie aussi la forme fermée z² / (n + z²) de la borne haute quand il n'y a aucun succès, et le minimum de 125 questions sans échec pour passer la barrière de 3 % (point 2).
6. La taille d'échantillon de 865 questions est vérifiée, avec la valeur exacte 864,36 avant arrondi.
7. Une barrière sans aucune question doit lever `ValueError` ; sinon `raise AssertionError` arrête le programme.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`wald(succes, n, z)`** — Cette fonction est le témoin à charge du programme, un géomètre pressé qui trace son intervalle à la règle sans vérifier qu'il reste sur le terrain : elle reçoit le nombre de succès, le nombre de questions et le coefficient z, 1,96 par défaut, calcule la proportion p = succès / n et la demi-largeur z √(p(1 − p) / n), puis renvoie le couple (p − demi, p + demi) sans jamais le ramener dans [0, 1]. Elle exhibe ainsi les deux défauts de l'intervalle naïf : une largeur nulle pour 0 succès sur 150, comme si l'on était certain, et une borne haute de 1,0058 pour 47 sur 50, au-dessus de toute proportion possible.

**`taille_echantillon(p, marge, z)`** — Elle répond à la question du responsable d'évaluation qui prépare sa campagne : combien de questions faut-il étiqueter pour mesurer une proportion à la marge voulue ? La fonction reçoit la proportion attendue, la marge d'erreur acceptée et le coefficient z, 1,96 par défaut, applique la formule de l'étape 7, z² p (1 − p) / e², puis arrondit au-dessus avec `math.ceil`, puisqu'on ne pose pas une demi-question. Elle renvoie cet entier : 865 questions pour mesurer 0,90 à plus ou moins 0,02, la valeur exacte avant arrondi étant 864,36.

**`Barriere.intervalle()`** — Cette méthode est l'huissier qui constate, chiffres en main, où se situe réellement une proportion mesurée : elle ne reçoit rien d'autre que la barrière elle-même, appelle `wilson` avec ses succès et son nombre de questions, et lève `ValueError` si `wilson` renvoie `None`, c'est-à-dire si la barrière ne compte aucune question, pour qu'une mesure absente ne puisse jamais passer par défaut. Sinon, elle renvoie l'intervalle de Wilson à 95 % sous la forme d'un couple (borne basse, borne haute) ; pour les 183 réponses fidèles sur 200 de la banque, il va de 0,8681 à 0,9463.

**`Barriere.passe()`** — C'est le contrôleur au portillon, qui laisse passer ou retient selon l'exigence inscrite sur la barrière : la méthode demande l'intervalle à `intervalle`, puis, si le sens vaut « min », vérifie que la borne basse atteint le seuil, et, si le sens vaut « max », que la borne haute reste sous le seuil ; tout autre sens lève `ValueError`. Elle renvoie un booléen ; ainsi la banque, avec 0,915 observé mais une borne basse de 0,8681, échoue face au seuil de 0,90, tandis que la crypto, avec 0 version remplacée citée sur 150, passe sous le plafond de 3 % grâce à une borne haute de 0,025.

**`Domaine.decision()`** — Cette méthode est le comité de déploiement d'un domaine, qui ne donne son feu vert que si tous les voyants sont au vert : elle parcourt les barrières du domaine, demande à chacune si elle `passe`, et renvoie « déployer » seulement si toutes passent, « bloquer » dès qu'une seule échoue. Sur la campagne illustrative, l'immobilier, la crypto, l'assurance et les ressources humaines sont déployés, alors que la banque, le BTP et le secteur public sont bloqués, ce dernier à cause du seul HitRate@3 en arabe, dont la borne basse de 0,7939 manque de peu le seuil de 0,80.

**`tableau_de_bord()`** — Cette fonction est le recueil de la campagne d'évaluation, avec ses comptes inventés pour l'exemple : elle ne reçoit rien et renvoie la liste des sept domaines, de la banque au secteur public, chacun décrit par sa fonction de score, son mode de découpage, ses barrières et, le cas échéant, ses moyennes. Elle déclare en tout douze barrières, par exemple 190 succès sur 200 pour le HitRate@5 de la banque ou 96 sur 120 pour le bon contrat au rang 1 du BTP, ainsi que des moyennes comme un MRR@5 de 0,82, qui seront affichées à part, sans intervalle.

**`main()`** — Le chef d'orchestre imprime d'abord une ligne par barrière, avec la proportion observée, l'intervalle de Wilson, l'exigence et le résultat, et vérifie les douze intervalles et les douze verdicts. Il affiche et vérifie ensuite les sept décisions, recalcule le paradoxe de la banque, bloquée à 0,915 au-dessus du seuil, avec le dénominateur 1,019208, le centre 0,9072 et la demi-largeur 0,0391, puis montre les moyennes sans intervalle, le suivi trop maigre de l'assureur (22 sur 29, de 0,5789 à 0,8778), le contre-exemple de Wald, le minimum de 125 questions sans échec pour passer une barrière de 3 %, la taille d'échantillon de 865, et enfin le refus d'une barrière vide par `ValueError`. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 30 — Tableau de bord RAG par domaine : barrières de déploiement sur intervalles de Wilson, moyennes à part."""
import math
import sys
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def wald(succes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalle « normal » naïf p ± z·sqrt(p(1 − p)/n), SANS écrêtage : gardé pour le contre-exemple."""
    p = succes / n
    demi = z * math.sqrt(p * (1 - p) / n)
    return (p - demi, p + demi)


def taille_echantillon(p: float, marge: float, z: float = 1.96) -> int:
    """n = z² p (1 − p) / e², arrondi à l'entier supérieur (formule démontrée à l'étape 7)."""
    return math.ceil(z * z * p * (1 - p) / (marge * marge))


@dataclass
class Barriere:
    """Une proportion mesurée sur n questions, et l'exigence qu'elle doit satisfaire avant un déploiement."""
    nom: str
    succes: int
    n: int
    seuil: float
    sens: str                 # "min" : la borne BASSE doit atteindre le seuil ; "max" : la borne HAUTE doit rester dessous

    def intervalle(self) -> tuple[float, float]:
        ic = wilson(self.succes, self.n)
        if ic is None:
            raise ValueError(f"{self.nom} : aucune question, la barrière ne peut pas être évaluée")
        return ic

    def passe(self) -> bool:
        lo, hi = self.intervalle()
        if self.sens == "min":
            return lo >= self.seuil
        if self.sens == "max":
            return hi <= self.seuil
        raise ValueError("sens doit valoir 'min' ou 'max'")


@dataclass
class Domaine:
    nom: str
    fonction_score: str       # ce qui classe les morceaux à chaque requête
    decoupage: str            # comment les documents sont coupés en morceaux
    barrieres: list[Barriere]
    moyennes: dict[str, float] = field(default_factory=dict)   # MRR, NDCG, P@k : des moyennes, pas des proportions

    def decision(self) -> str:
        return "déployer" if all(b.passe() for b in self.barrieres) else "bloquer"


def tableau_de_bord() -> list[Domaine]:
    """Campagne d'évaluation illustrative : les comptes sont inventés pour l'exemple, pas mesurés."""
    return [
        Domaine("BANQUE", "BM25 + cosinus, RRF, reranker", "un article de politique par morceau, titre répété",
                [Barriere("HitRate@5", 190, 200, 0.90, "min"), Barriere("réponses fidèles", 183, 200, 0.90, "min")],
                {"MRR@5": 0.82}),
        Domaine("IMMO", "filtre quartier et type, puis cosinus", "une transaction par morceau",
                [Barriere("estimations fiables", 168, 190, 0.80, "min")], {"NDCG@5": 0.84}),
        Domaine("CRYPTO", "BM25 + cosinus, RRF, filtre « en vigueur »", "une section par morceau, avec sa version",
                [Barriere("HitRate@3", 141, 150, 0.85, "min"), Barriere("version remplacée citée", 0, 150, 0.03, "max")],
                {"MRR@3": 0.81}),
        Domaine("ASSUR", "cosinus + reranker, filtre version du contrat", "une clause par morceau",
                [Barriere("réponses fidèles", 271, 300, 0.85, "min")], {"NDCG@5": 0.91}),
        Domaine("RH", "filtre par régime, puis BM25 + cosinus", "une règle par morceau, régime en métadonnée",
                [Barriere("HitRate@3", 138, 150, 0.85, "min"), Barriere("réponse sans régime", 0, 150, 0.03, "max")],
                {"P@4": 0.78}),
        Domaine("BTP", "BM25 + cosinus, RRF, filtre par lot", "une clause de contrat par morceau, lot en métadonnée",
                [Barriere("bon contrat au rang 1", 96, 120, 0.75, "min")], {"MRR@3": 0.86}),
        Domaine("PUBLIC", "BM25 sur texte normalisé + cosinus multilingue", "une page de démarche par langue",
                [Barriere("HitRate@3 en arabe", 170, 200, 0.80, "min"), Barriere("HitRate@3 en anglais", 184, 200, 0.80, "min"),
                 Barriere("abstention hors champ", 47, 50, 0.80, "min")]),
    ]


def main() -> None:
    domaines = tableau_de_bord()
    print("Barrière                          observé            IC 95 % de Wilson    exigence             résultat")
    attendus = []
    for dom in domaines:
        for b in dom.barrieres:
            lo, hi = b.intervalle()
            exigence = ("borne basse ≥ " if b.sens == "min" else "borne haute ≤ ") + f"{b.seuil:.2f}"
            observe = f"{b.succes}/{b.n} = {b.succes / b.n:.3f}"
            print(f"{dom.nom:<8} {b.nom:<24} {observe:>17}  [{lo:.4f} ; {hi:.4f}]    {exigence:<20} {'passe' if b.passe() else 'échoue'}")
            attendus.append((round(lo, 4), round(hi, 4), b.passe()))
    assert attendus == [
        (0.9104, 0.9726, True), (0.8681, 0.9463, False),                         # BANQUE
        (0.8309, 0.9223, True),                                                # IMMO
        (0.8899, 0.9681, True), (0.0, 0.025, True),                            # CRYPTO
        (0.8646, 0.9319, True),                                                # ASSUR
        (0.8654, 0.9536, True), (0.0, 0.025, True),                            # RH
        (0.7196, 0.8618, False),                                               # BTP
        (0.7939, 0.8929, False), (0.874, 0.9502, True), (0.8378, 0.9794, True),  # PUBLIC
    ]

    decisions = {d.nom: d.decision() for d in domaines}
    print("Décisions : " + " · ".join(f"{nom} {dec}" for nom, dec in decisions.items()))
    assert decisions == {"BANQUE": "bloquer", "IMMO": "déployer", "CRYPTO": "déployer", "ASSUR": "déployer",
                         "RH": "déployer", "BTP": "bloquer", "PUBLIC": "bloquer"}
    banque = domaines[0].barrieres[1]
    assert banque.succes / banque.n > banque.seuil and not banque.passe()     # 0,915 > 0,90, et pourtant bloqué
    z2 = 1.96 ** 2
    den = 1 + z2 / 200
    centre = (0.915 + z2 / 400) / den
    demi = 1.96 * math.sqrt(0.915 * 0.085 / 200 + z2 / (4 * 200 * 200)) / den
    assert (round(den, 6), round(centre, 4), round(demi, 4), round(centre - demi, 4)) == (1.019208, 0.9072, 0.0391, 0.8681)

    print("Moyennes (pas de Wilson) : " + " · ".join(f"{d.nom} {k} {v:.2f}" for d in domaines for k, v in d.moyennes.items()))

    revues = Barriere("revues confirmées", 22, 29, 0.0, "min")
    lo, hi = revues.intervalle()
    print(f"Suivi ASSUR : revues confirmées 22/29 = {22 / 29:.3f}, IC [{lo:.4f} ; {hi:.4f}] : 29 cas ne suffisent pas à juger le garde-fou")
    assert (round(lo, 4), round(hi, 4)) == (0.5789, 0.8778) and hi - lo > 0.29

    w0, w47 = wald(0, 150), wald(47, 50)
    print(f"Wald contre Wilson : 0/150 → [{w0[0]:.4f} ; {w0[1]:.4f}] contre [0.0000 ; {wilson(0, 150)[1]:.4f}] ; "
          f"47/50 → borne haute de Wald {w47[1]:.4f}, au-dessus de 1")
    assert w0 == (0.0, 0.0) and w47[1] > 1 and wilson(47, 50)[1] < 1
    assert abs(wilson(0, 150)[1] - z2 / (150 + z2)) < 1e-12 and round(z2 / (150 + z2), 4) == 0.025   # z²/(n + z²)
    assert wilson(0, 150)[0] == 0.0 and wilson(0, 0) is None
    n_min = next(n for n in range(1, 1000) if wilson(0, n)[1] <= 0.03)      # questions sans échec pour passer « ≤ 3 % »
    assert n_min == 125 and round(z2 * (1 / 0.03 - 1), 2) == 124.21

    n_requis = taille_echantillon(0.90, 0.02)
    print(f"Taille d'échantillon pour ±0.02 autour de 0.90 : {n_requis} questions")
    assert n_requis == 865 and round(z2 * 0.9 * 0.1 / 0.02 ** 2, 2) == 864.36

    try:
        Barriere("vide", 0, 0, 0.9, "min").passe()
    except ValueError:
        pass
    else:
        raise AssertionError("une barrière sans question ne doit pas passer")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Barrière                          observé            IC 95 % de Wilson    exigence             résultat
BANQUE   HitRate@5                  190/200 = 0.950  [0.9104 ; 0.9726]    borne basse ≥ 0.90   passe
BANQUE   réponses fidèles           183/200 = 0.915  [0.8681 ; 0.9463]    borne basse ≥ 0.90   échoue
IMMO     estimations fiables        168/190 = 0.884  [0.8309 ; 0.9223]    borne basse ≥ 0.80   passe
CRYPTO   HitRate@3                  141/150 = 0.940  [0.8899 ; 0.9681]    borne basse ≥ 0.85   passe
CRYPTO   version remplacée citée      0/150 = 0.000  [0.0000 ; 0.0250]    borne haute ≤ 0.03   passe
ASSUR    réponses fidèles           271/300 = 0.903  [0.8646 ; 0.9319]    borne basse ≥ 0.85   passe
RH       HitRate@3                  138/150 = 0.920  [0.8654 ; 0.9536]    borne basse ≥ 0.85   passe
RH       réponse sans régime          0/150 = 0.000  [0.0000 ; 0.0250]    borne haute ≤ 0.03   passe
BTP      bon contrat au rang 1       96/120 = 0.800  [0.7196 ; 0.8618]    borne basse ≥ 0.75   échoue
PUBLIC   HitRate@3 en arabe         170/200 = 0.850  [0.7939 ; 0.8929]    borne basse ≥ 0.80   échoue
PUBLIC   HitRate@3 en anglais       184/200 = 0.920  [0.8740 ; 0.9502]    borne basse ≥ 0.80   passe
PUBLIC   abstention hors champ        47/50 = 0.940  [0.8378 ; 0.9794]    borne basse ≥ 0.80   passe
Décisions : BANQUE bloquer · IMMO déployer · CRYPTO déployer · ASSUR déployer · RH déployer · BTP bloquer · PUBLIC bloquer
Moyennes (pas de Wilson) : BANQUE MRR@5 0.82 · IMMO NDCG@5 0.84 · CRYPTO MRR@3 0.81 · ASSUR NDCG@5 0.91 · RH P@4 0.78 · BTP MRR@3 0.86
Suivi ASSUR : revues confirmées 22/29 = 0.759, IC [0.5789 ; 0.8778] : 29 cas ne suffisent pas à juger le garde-fou
Wald contre Wilson : 0/150 → [0.0000 ; 0.0000] contre [0.0000 ; 0.0250] ; 47/50 → borne haute de Wald 1.0058, au-dessus de 1
Taille d'échantillon pour ±0.02 autour de 0.90 : 865 questions
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : on ne déploie pas un agent RAG sur une impression. On le déploie quand chaque proportion qui compte a une borne de Wilson du bon côté de son seuil, et l'on garde les moyennes et les petits échantillons pour le suivi.

## Squelette algorithmique

Le tableau de bord de ce fichier applique, domaine par domaine, des barrières chiffrées : chaque barrière est un taux mesuré, avec un sens (« au moins » ou « au plus ») et un seuil, jugé par son intervalle de Wilson plutôt que par sa seule valeur.

```text
ALGORITHME TableauDeBordRAG
ENTRÉES : pour chaque domaine : barrières (nom, succès s, total n, seuil, sens ∈ {min, max}), z
SORTIE  : pour chaque barrière : taux, intervalle, verdict ; et la taille d'échantillon conseillée

  POUR CHAQUE domaine FAIRE
      POUR CHAQUE barrière FAIRE
          p̂ ← s / n
          (bas, haut) ← Wilson(s, n, z)
          SI sens = min ALORS verdict ← (bas ≥ seuil)      (on doit prouver qu'on est au-dessus)
          SI sens = max ALORS verdict ← (haut ≤ seuil)     (on doit prouver qu'on est en dessous)
      FIN POUR
  FIN POUR
  n_conseillé(p, marge) ← ⌈ z² p (1 − p) / marge² ⌉
```

**Complexité.** Chaque barrière coûte O(1) : un quotient, un intervalle et une comparaison. Le tableau entier coûte O(B) pour B barrières, quel que soit le nombre de questions déjà évaluées, puisque seuls les comptes s et n sont conservés.

**Du squelette au code.** `wilson` donne l'intervalle (et `wald` l'intervalle naïf, gardé pour comparaison), `taille_echantillon` la dernière ligne, et `tableau_de_bord` construit la liste des domaines et de leurs barrières que `main` évalue et affiche.

## Cas d'usage réels aux Émirats

Les comptes, seuils et moyennes ci-dessous sont ceux, illustratifs, du tableau de bord ; ils ne décrivent aucun système réel.

### Banque — un bon moteur, une fidélité pas encore prouvée

Une banque de détail de Dubaï prépare la mise en production de l'assistant crédit de ses conseillers, qui répond à partir de sa politique interne et des règles de la CBUAE découpées article par article, avec le titre de la section répété dans chaque morceau pour qu'un morceau isolé reste compréhensible. La recherche fusionne BM25 et cosinus par RRF, puis un reranker retrie les vingt premiers candidats. Sur un jeu de 200 questions annotées, le HitRate@5 vaut 190 sur 200 et sa borne basse de Wilson, 0,9104, dépasse le seuil de 0,90 : la recherche est prouvée suffisante. La fidélité des réponses vaut 183 sur 200, soit 0,915, mais sa borne basse n'est que de 0,8681 : l'équipe ne peut pas affirmer que plus de 90 % des réponses sont fidèles, et le domaine est bloqué. Elle a deux options chiffrées : améliorer la génération (consigne plus stricte, citations obligatoires, garde-fou de fidélité en ligne) ou agrandir le jeu d'évaluation vers 865 questions pour mesurer à ± 0,02 près. Déployer sur la seule valeur observée, c'est accepter qu'une réponse sur dix puisse appliquer un plafond d'endettement faux, alors que la CBUAE limite le ratio total à 50 % du revenu (30 % pour un retraité). En production, on suivra la part de réponses fidèles sur un échantillon hebdomadaire, avec son intervalle, et le MRR@5, qui vaut aujourd'hui 0,82.

### Immobilier — des estimations qui savent dire « peu fiable »

Une agence qui opère à Dubaï et à Abu Dhabi alimente son agent d'estimation avec son historique de transactions, une transaction par morceau, sous forme de fiche structurée : quartier, type de bien, surface en sqft, date et prix en AED/sqft. La recherche filtre d'abord par quartier et par type, puis classe par cosinus, parce qu'un comparable d'un autre quartier fausse l'estimation quelle que soit sa proximité sémantique. Une estimation est dite fiable quand au moins trois comparables notés 2 ou 3 figurent dans le top-5 ; c'est le cas pour 168 requêtes sur 190, avec une borne basse de 0,8309 au-dessus du seuil de 0,80, et le domaine est déployé. Pour les autres requêtes, l'agent ne donne pas de chiffre sec : il annonce une estimation peu fiable et le nombre de comparables utilisés. Le NDCG@5 moyen, 0,84, est suivi à part, comme une moyenne, pour voir si l'ordre des comparables se dégrade. Une estimation d'agent reste indicative, et elle doit rappeler que l'acheteur paiera aussi 4 % de frais de transfert au DLD. On suit la part d'estimations fiables par quartier et l'écart médian entre l'estimation et le prix final de vente.

### Crypto — prouver qu'une erreur rare reste rare

Une plateforme d'actifs virtuels agréée par la VARA indexe ses procédures internes et ses grilles de frais par section, chaque morceau portant l'identifiant de sa version, et la recherche écarte les versions remplacées avant de fusionner BM25 et cosinus par RRF. Sur 150 questions, le HitRate@3 vaut 141, avec une borne basse de 0,8899 au-dessus du seuil de 0,85. La seconde barrière porte sur l'erreur que la plateforme redoute le plus, citer une grille remplacée : 0 cas sur 150. La démonstration montre qu'un zéro observé ne vaut pas un risque nul ; il garantit seulement, à 95 %, un taux d'au plus 2,5 %, juste sous le seuil de 3 %, et il fallait au moins 125 questions pour pouvoir l'affirmer. Les deux barrières passent et le domaine est déployé, avec un MRR@3 moyen de 0,81 suivi à part. Une plateforme agréée doit communiquer des conditions exactes et à jour, d'où une barrière exprimée comme un plafond d'erreur plutôt que comme un taux de réussite. En production, chaque nouvelle grille de frais déclenche une nouvelle campagne de vérification avant d'être servie aux clients.

### Assurance — une barrière qui passe, un suivi qui ne prouve encore rien

Un assureur auto et santé découpe ses contrats clause par clause (garanties, exclusions, franchises) et filtre la recherche sur la version du contrat signée par l'assuré avant de classer par cosinus et de retrier par un reranker. Sur 300 sinistres annotés, 271 réponses sont fidèles, soit 0,903 ; la borne basse de 0,8646 dépasse le seuil de 0,85, et le domaine est déployé, avec un NDCG@5 moyen de 0,91. En ligne, toute réponse dont une phrase n'est pas étayée part en revue humaine, comme la franchise inventée de l'étape 29. L'équipe voudrait savoir si ce garde-fou se trompe souvent : sur les 29 revues de la campagne, 22 confirment une vraie erreur, mais l'intervalle de 0,5789 à 0,8778 est trop large pour conclure, et l'indicateur reste un suivi. Un garde-fou trop zélé surcharge les gestionnaires, un garde-fou trop laxiste laisse passer des paiements faux ; l'assurance étant supervisée par la CBUAE, chaque décision de sinistre doit rester justifiable par la clause applicable. On attend quelques centaines de revues avant de transformer cette précision en barrière.

### RH — ne jamais répondre sans connaître le régime

Un cabinet RH présent dans plusieurs émirats découpe ses règles une par une et attache à chaque morceau son régime juridique : secteur privé fédéral (décret-loi fédéral 33/2021), DIFC, ressortissants émiriens relevant de la GPSSA. La recherche filtre d'abord sur le régime du salarié, puis fusionne BM25 et cosinus. Sur 150 questions, le HitRate@3 vaut 138, avec une borne basse de 0,8654 au-dessus du seuil de 0,85. La seconde barrière interdit de répondre quand le régime du salarié est inconnu : aucune réponse de ce type sur 150, soit une borne haute de 0,0250 sous le plafond de 3 %, et le domaine est déployé. La Precision@4 moyenne, 0,78, rappelle qu'un contexte sur cinq contient encore un morceau inutile, ce que l'étape 26 a montré dangereux quand ce morceau vient d'un autre régime. Une indemnité de fin de service calculée selon le mauvais régime crée un litige, et chaque réponse reste à confirmer avec le texte en vigueur avant un versement. On suit le HitRate@3 et la Precision@4 par régime.

### BTP — un pilote sous revue humaine plutôt qu'un déploiement

Un groupe de construction qui mène de grands chantiers à Dubaï découpe ses contrats de sous-traitance clause par clause, avec l'identifiant du lot en métadonnée, et son agent de contrôle des factures lit la première clause renvoyée pour appliquer la retenue de garantie. La barrière porte donc sur le Success@1 : le bon contrat est au rang 1 pour 96 questions sur 120, soit 0,80, mais la borne basse de 0,7196 reste sous le seuil de 0,75, et le domaine est bloqué. Le MRR@3 moyen de 0,86 montre que le bon contrat est presque toujours dans les trois premiers, ce qui oriente la correction : un reranker, ou un filtre plus strict sur le lot, devrait le faire remonter en tête. En attendant, l'équipe lance un pilote où chaque facture est validée par un contrôleur, ce qui permet aussi d'enrichir le jeu d'évaluation. Une retenue mal appliquée fausse le montant versé au sous-traitant et la TVA de 5 % qui s'y rapporte, et sa régularisation coûte plus cher qu'une revue préalable. On suivra le Success@1 par lot, avec son intervalle, à chaque nouvelle campagne.

### Secteur public — une langue bloque le déploiement

Une entité de services publics en ligne, accessible par UAE Pass, indexe chaque page de démarche séparément en arabe et en anglais, normalise l'arabe (formes de l'alef, ta marbuta, diacritiques) avant BM25 et utilise un cosinus multilingue. Sur 200 questions par langue, le HitRate@3 vaut 184 en anglais, avec une borne basse de 0,8740, mais seulement 170 en arabe, avec une borne basse de 0,7939, juste sous le seuil de 0,80. Le test d'abstention passe : sur 50 questions hors périmètre, 47 abstentions correctes, avec une borne basse de 0,8378. Le domaine est bloqué par sa seule barrière arabe, parce qu'un service public doit offrir la même qualité de réponse dans les deux langues et qu'une moyenne des deux langues aurait masqué l'écart. L'analyse porte sur les noms de démarches translittérés de plusieurs façons, que la normalisation actuelle ne rapproche pas. On suit le HitRate@3 séparément par langue et l'écart entre les deux, à chaque nouvelle version de l'index.

## Pièges et limites

- **Décider sur la valeur observée.** Une proportion de 0,915 sur 200 questions ne prouve pas qu'on dépasse 0,90 ; seule la borne de Wilson le dit (démonstration, point 1).
- **Lire un zéro comme une garantie.** Zéro échec sur 150 questions garantit seulement, à 95 %, un taux d'au plus 2,5 % ; il en faut au moins 125 pour passer une barrière de 3 % (point 2).
- **Mettre un intervalle de Wilson sur une moyenne.** Un MRR ou un NDCG moyen n'est pas une proportion de succès ; on fonde les barrières sur des proportions comptables et l'on suit les moyennes à part (point 3).
- **Moyenner des sous-populations qui doivent chacune passer.** Une moyenne des langues, des régimes ou des lots masque celui qui échoue : chaque sous-population a sa barrière.
- **Oublier que les questions ne sont pas indépendantes.** Wilson suppose des essais indépendants ; cinquante variantes d'une même question comptent presque pour une. Le jeu d'évaluation doit couvrir des questions réellement différentes.

### Exercice feuille blanche

1. Sans regarder le code, écrire `wilson` à partir de la formule, puis retrouver la borne basse 0,8681 pour 183 succès sur 200.
2. Prédire, puis vérifier : avec 0 échec observé, combien de questions faut-il pour garantir un taux d'erreur d'au plus 1 % ? (Réponse : il faut z² / (n + z²) ≤ 0,01, donc n ≥ 99 × 3,8416 ≈ 380,32, soit 381 questions.)
3. Trouver le bug : dans `passe()`, on remplace les bornes par la proportion observée, `p = self.succes / self.n`, puis `return p >= self.seuil if self.sens == "min" else p <= self.seuil`. Quels domaines changent de décision ? (Réponse : la banque, avec 0,915 au-dessus de 0,90, le BTP, avec 0,80 au-dessus de 0,75, et le secteur public, avec 0,85 au-dessus de 0,80 en arabe, passent à « déployer ». Les sept domaines sont alors déployés et les trois blocages disparaissent, sans aucune preuve supplémentaire.)

> Suite : [Reranking par cross-encodeur](<30b-RAG-Reranking-Cross-Encodeur.md>) — étape 30 bis.
