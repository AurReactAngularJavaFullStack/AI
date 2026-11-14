# Palier 06 — La mémoire

> Palier 06 sur 12 · Précédent : [Palier 05 — Boucle d'agent](<../05-Boucle-d-Agent/README.md>) · Suivant : [Palier 07 — Recherche hybride](<../07-Recherche-Hybride/README.md>) · Leçons à relire : [Étape 14 — Similarité cosinus](<../../04-Contexte-Similarite-et-Memoire/14-Similarite-Cosinus-RAG-et-Memoire.md>) · [Étape 15 bis — Mémoire, définitions](<../../04-Contexte-Similarite-et-Memoire/15b-Memoire-Definitions-Fondamentaux.md>) · [Étape 16 — Décroissance temporelle](<../../04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md>) · [Étape 17 — Score de pertinence](<../../04-Contexte-Similarite-et-Memoire/17-Memoire-Formule-Score-de-Pertinence.md>) · [Étape 77 — Projet final](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Démonstrations : [27 — Score de mémoire](<../../Demonstrations/05-Contexte/27_score_memoire.md>) · [03 — Similarité cosinus](<../../Demonstrations/02-Vecteurs/03_similarite_cosinus.md>)

## Où en est l'agent

À la fin du palier 05, l'agent sait agir : `executer_agent` fait parler le modèle et les outils jusqu'à un arrêt garanti. Mais il oublie tout d'une question à l'autre. Le client C-1 qui demande une hypothèque doit redonner son salaire et son crédit en cours, alors qu'il les a déclarés il y a trois mois. Le modèle de langage, lui, ne retient rien d'un appel à l'autre : la mémoire est un composant du programme, pas du modèle.

Ce palier écrit `agent/memoire.py`. À partir de la question, il choisit, parmi tous les souvenirs du client, les k qui méritent une place dans le prompt.

```text
                         ┌──────────────────────────── paquet agent/ ─────────────────────────────┐
                         │   ╔══════════════════════════════════════════════════════════════╗     │
  question ─────────────►│   ║  memoire.rappeler                         PALIER 06 (ICI)    ║     │
  souvenirs du client ──►│   ║   cosinus · recence · min_max · score_pertinence → top k     ║     │
  plonger_texte (07) ───►│   ║   puis relecture : jour_acces ← jour                         ║     │
                         │   ╚══════════════════════════════════════════════════════════════╝     │
                         │            │ textes des k souvenirs gardés                              │
                         │            ▼                                                            │
                         │   modele.construire_prompt (01) ── système <memoire>…</memoire>, message│
                         │            │                                                            │
                         │            ▼                                                            │
                         │   boucle.executer_agent (05) ──► outils.executer_appel (04) ──► metier  │
                         └─────────────────────────────────────────────────────────────────────────┘
```

Dans la boucle percevoir → décider → agir → observer, la mémoire sert deux fois. Avant le premier tour, elle enrichit ce que l'agent **perçoit** : `construire_prompt(question, [s.texte for _, s in gardes], documents)` place les souvenirs gardés dans la balise `<memoire>` du prompt système. Après le rappel, elle **observe** qu'un souvenir a servi : sa date de dernier accès passe au jour courant, ce qui le remet à neuf pour la question suivante.

## Ce que tu vas coder

- `cosinus(a, b)` : la similarité cosinus de deux vecteurs, qui refuse un vecteur nul.
- `min_max(valeurs)` : ramène une liste de nombres dans [0, 1], avec 0 partout si toutes les valeurs sont égales.
- `recence(age, demi_vie)` : la décroissance exponentielle d'un souvenir, qui vaut 1 à l'âge 0 et 1/2 à la demi-vie.
- `score_pertinence(sim, rec, imp, poids)` : la somme pondérée des trois composantes, qui refuse des poids ou des composantes qui sortiraient le score de [0, 1].
- `Souvenir` : une `dataclass` avec un texte, un jour de dernier accès et une importance de 1 à 10, vérifiée à la construction.
- `rappeler(question, souvenirs, plonger_texte, jour, k=2, demi_vie=30.0, poids=(0.5, 0.3, 0.2))` : les k souvenirs les plus pertinents, avec leur score, et leur relecture.

## Rappel de cours

Le score d'un souvenir mélange trois signaux : sa proximité de sens avec la question, sa fraîcheur et son importance. Chaque signal a sa formule, et le mélange en a une quatrième.

La similarité cosinus (étape 14) : le cosinus de l'angle entre deux vecteurs de dimension d.

$$
\cos(a, b) = \frac{a \cdot b}{\lVert a \rVert \, \lVert b \rVert} = \frac{\sum_{i=1}^{d} a_i b_i}{\sqrt{\sum_{i=1}^{d} a_i^{2}} \; \sqrt{\sum_{i=1}^{d} b_i^{2}}}
$$

La normalisation min-max (étape 17), calculée sur l'ensemble des souvenirs candidats, avec la convention x̃ⱼ = 0 pour tous les j quand toutes les valeurs sont égales :

$$
\widetilde{x}_j = \frac{x_j - \min_i x_i}{\max_i x_i - \min_i x_i}
$$

La récence (étape 16) : une décroissance exponentielle de l'âge, réglée par la demi-vie.

$$
rec(\Delta t) = e^{-\lambda\,\Delta t} = 2^{-\Delta t / t_{1/2}} \qquad \text{avec} \qquad \lambda = \frac{\ln 2}{t_{1/2}}
$$

Le score de pertinence (étape 17) : une combinaison convexe des trois composantes normalisées.

$$
S_j = w_{sim}\,\widetilde{sim}_j + w_{rec}\,\widetilde{rec}_j + w_{imp}\,\widetilde{imp}_j
$$

$$
w_{sim} \ge 0, \quad w_{rec} \ge 0, \quad w_{imp} \ge 0, \qquad w_{sim} + w_{rec} + w_{imp} = 1
$$

### Les symboles, un par un

$$
a, \; b
$$

Deux vecteurs de même dimension : le plongement de la question et celui d'un souvenir. En Python, deux `list[float]`.

$$
d
$$

La dimension des vecteurs, le nombre de concepts. Elle vaut 8 dans le scénario du crédit : dette, revenu, crédit, durée, taxe, change, emploi, immobilier.

$$
a \cdot b
$$

Le produit scalaire, la somme des produits terme à terme. En Python : `sum(x * y for x, y in zip(a, b))`.

$$
\lVert a \rVert
$$

La norme, la longueur du vecteur. En Python : `math.sqrt(sum(x * x for x in a))`. Une norme nulle rend le cosinus indéfini.

$$
x_j, \; \widetilde{x}_j
$$

La valeur brute d'une composante pour le souvenir j, et sa valeur ramenée dans [0, 1]. En Python : un élément de la liste passée à `min_max`, et l'élément de même rang de la liste rendue.

$$
\Delta t
$$

L'âge du souvenir, en jours, depuis son dernier accès : `jour - s.jour_acces`. Il est toujours ≥ 0.

$$
t_{1/2}
$$

La demi-vie, en jours : l'âge auquel la récence vaut 1/2. En Python : `demi_vie`, 30 par défaut.

$$
\lambda
$$

Le taux de décroissance, en jours⁻¹ : ln 2 / 30 ≈ 0,0231 par jour pour une demi-vie de 30 jours. En Python : `lam`.

$$
w_{sim}, \; w_{rec}, \; w_{imp}
$$

Les poids de la similarité, de la récence et de l'importance. Ils sont positifs et de somme 1. En Python : le triplet `poids`, qui vaut (0,5 ; 0,3 ; 0,2) par défaut.

$$
S_j
$$

Le score du souvenir j, dans [0, 1]. En Python : le premier élément de chaque couple rendu par `rappeler`.

$$
k
$$

Le nombre de souvenirs gardés pour le prompt. En Python : `k`, 2 par défaut.

**Pourquoi le cosinus reste dans [−1, 1].** L'inégalité de Cauchy-Schwarz donne |a · b| ≤ ‖a‖ ‖b‖ (étape 14, démonstration 1). Le quotient est donc entre −1 et 1 en mathématiques. En flottant, il peut sortir de très peu : pour les vecteurs colinéaires [1, 1, 1] et [2, 2, 2], le quotient calculé vaut 1,0000000000000002. On le borne donc avec `max(-1.0, min(1.0, …))`. Un vecteur nul n'a pas de direction, et la formule divise par zéro : on lève `ValueError`, sans epsilon qui cacherait le problème.

**Pourquoi min-max garde l'ordre.** On note lo et hi le plus petit et le plus grand des xᵢ, avec hi > lo. L'application x ↦ (x − lo) / (hi − lo) est affine de pente 1 / (hi − lo) > 0, donc croissante : elle ne change le classement d'aucune composante prise seule. Elle envoie lo sur 0 et hi sur 1, donc toutes les valeurs dans [0, 1]. Et elle ne dépend pas de l'unité : une importance notée sur 100 au lieu de 10 donne la même liste (étape 17, démonstration 2).

**Pourquoi la demi-vie donne λ.** On cherche l'âge t½ tel que la récence vaille 1/2 :

$$
e^{-\lambda t_{1/2}} = \frac{1}{2} \;\Longleftrightarrow\; -\lambda\,t_{1/2} = -\ln 2 \;\Longleftrightarrow\; \lambda = \frac{\ln 2}{t_{1/2}}
$$

Après k demi-vies, il reste 1/2ᵏ : avec t½ = 30 jours, un souvenir de 90 jours pèse 1/8 = 0,125 de sa valeur neuve.

**Pourquoi le score reste dans [0, 1].** Chaque composante est dans [0, 1] après min-max, et chaque poids est ≥ 0. Donc 0 ≤ wᵢ x̃ᵢ ≤ wᵢ pour chaque composante, et en sommant, S est compris entre 0 et la somme des poids, qui vaut 1. Les deux hypothèses sont nécessaires. Avec des poids (0,5 ; 0,5 ; 0,5), de somme 1,5, un souvenir parfait vaudrait 1,5. Avec (0,6 ; 0,6 ; −0,2), un souvenir (0, 0, 1) vaudrait −0,2. C'est pourquoi `score_pertinence` les refuse.

**Pourquoi normaliser avant de pondérer.** Une importance brute de 1 à 10 a une étendue de 9, et un cosinus une étendue d'au plus 1. Avec le poids 0,2, l'importance pèserait alors jusqu'à 1,8, contre 0,5 pour la similarité de poids 0,5 : le plus petit poids deviendrait la plus grande influence (étape 17, démonstration 1). Après min-max, les trois composantes ont la même étendue, 1, et les poids redeviennent les vraies influences.

## Spécification

Le module n'importe que la bibliothèque standard : `math`, `Callable` et `dataclass`. Il ne dépend d'aucun module antérieur.

### cosinus

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosinus(a, b)`** — Cette fonction doit être le navigateur qui compare deux caps sans se soucier de la longueur des trajets : elle reçoit deux vecteurs de même dimension, le plongement de la question et celui d'un souvenir, et renvoie le cosinus de l'angle qui les sépare, borné à l'intervalle [−1, 1]. Deux listes de longueurs différentes lèvent `ValueError` (« dimensions différentes »), et un vecteur de norme nulle, qui n'a pas de direction, lève `ValueError` (« vecteur nul : le cosinus n'est pas défini ») sans epsilon qui cacherait le problème. La question du crédit et le souvenir du salaire doivent donner 0,75, le souvenir du change environ 0,3536 ; c'est la composante « sens » du score de chaque souvenir.

```python
# [extrait] spécification
def cosinus(a: list[float], b: list[float]) -> float:
    """cos(a, b) = a · b / (‖a‖ ‖b‖), borné à [−1, 1] ; un vecteur nul lève ValueError (pas d'epsilon)."""
```

- Deux listes de longueurs différentes lèvent `ValueError("dimensions différentes")`.
- Un vecteur de norme nulle lève `ValueError`, avec le message `vecteur nul : le cosinus n'est pas défini`.
- Le résultat est borné à [−1, 1].

**Exemple chiffré.** On prend la question q = [1, 1, 2, 1, 0, 1, 0, 0] et le souvenir « salaire » v = [0, 1, 1, 0, 0, 0, 0, 0]. Le produit scalaire ne garde que les rangs où les deux vecteurs sont non nuls : q · v = 1 × 1 + 2 × 1 = 3. Les normes valent ‖q‖ = √(1 + 1 + 4 + 1 + 1) = √8 et ‖v‖ = √2. Donc cos = 3 / (√8 × √2) = 3 / √16 = 3 / 4 = 0,75. Pour le souvenir « change » w = [0, 0, 0, 0, 0, 3, 0, 0], on a q · w = 1 × 3 = 3 et ‖w‖ = 3, d'où cos = 3 / (3 × √8) = 1 / √8 ≈ 0,3536. Cas limites : [1, 0] et [0, 1] sont orthogonaux, cos = 0 ; [1, 2] et [2, 4] sont colinéaires, cos = 1 ; [1, 2] et [−1, −2] sont opposés, cos = −1. Tests : `TestCosinus`.

### min_max

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`min_max(valeurs)`** — Cette fonction doit jouer le rôle d'un arbitre qui ramène sur une même échelle de 0 à 1 des notes données par des juges aux barèmes différents : elle reçoit une liste de nombres et renvoie une liste de même longueur et de même ordre, où le plus petit devient 0, le plus grand 1, et chaque autre valeur se place proportionnellement entre les deux. Une liste vide lève `ValueError`, et si toutes les valeurs sont égales, elle renvoie 0.0 partout, puisqu'un signal constant ne départage personne. Les importances 9, 8, 4 et 2 doivent ainsi devenir 1, 6/7, 2/7 et 0, et la liste [3, 3] doit donner deux zéros.

```python
# [extrait] spécification
def min_max(valeurs: list[float]) -> list[float]:
    """x' = (x − min) / (max − min) ; si toutes les valeurs sont égales : 0.0 partout."""
```

- Une liste vide lève `ValueError` : le minimum d'une liste vide n'existe pas.
- Si toutes les valeurs sont égales, la formule diviserait par zéro. Un signal constant ne départage aucun candidat : on rend 0.0 partout, ce qui le retire du classement sans le fausser.
- Sinon, la liste rendue a la même longueur et le même ordre que la liste reçue.

**Exemple chiffré.** Les importances [9, 8, 4, 2] ont lo = 2 et hi = 9, donc hi − lo = 7. On obtient (9 − 2) / 7 = 1, (8 − 2) / 7 = 6/7 ≈ 0,857143, (4 − 2) / 7 = 2/7 ≈ 0,285714 et (2 − 2) / 7 = 0. Et [3, 3] donne [0.0, 0.0]. Tests : `TestMinMax`.

### recence

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`recence(age, demi_vie)`** — Cette fonction doit mesurer la fraîcheur d'un souvenir comme on mesure l'éclat d'une encre qui pâlit avec les jours : elle reçoit l'âge du souvenir en jours, depuis son dernier accès, et la demi-vie, puis renvoie une valeur de ]0, 1] qui vaut 1 à l'âge 0, 1/2 à la demi-vie et ne s'annule jamais. Un âge négatif, souvenir « du futur » qui trahit une horloge mal réglée, ou une demi-vie nulle ou négative, lèvent `ValueError`. Avec une demi-vie de 30 jours, elle doit renvoyer 0,5 à 30 jours, 0,125 à 90 jours et environ 0,8909 à 5 jours.

```python
# [extrait] spécification
def recence(age: float, demi_vie: float) -> float:
    """rec = e^(−λ · âge) avec λ = ln 2 / demi-vie : 1 à l'âge 0, 1/2 à la demi-vie."""
```

- Un âge négatif, ou une demi-vie ≤ 0, lève `ValueError`. Un âge négatif est un souvenir « du futur » : il trahit une horloge mal réglée, et sa récence dépasserait 1.
- Le résultat est dans ]0, 1] : il vaut 1 à l'âge 0 et ne s'annule jamais.

**Exemple chiffré**, avec t½ = 30 jours. On a λ = ln 2 / 30 = 0,693147 / 30 ≈ 0,023105 par jour. Les âges multiples de la demi-vie se calculent de tête : `recence(30, 30)` = 2⁻¹ = 0,5, et `recence(90, 30)` = 2⁻³ = 1/8 = 0,125. Pour 5 jours, `recence(5, 30)` = e^(−0,023105 × 5) = e^(−0,115525) = 2^(−1/6). Comme 2^(1/6) ≈ 1,122462, on obtient 1 / 1,122462 ≈ 0,8909. Tests : `TestRecence`.

### score_pertinence

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`score_pertinence(sim, rec, imp, poids)`** — Cette fonction doit être le jury qui additionne trois notes déjà mises sur la même échelle, chacune affectée de son coefficient : elle reçoit la similarité, la récence et l'importance normalisées, ainsi que le triplet des poids, et renvoie la somme pondérée, qui reste dans [0, 1]. Elle lève `ValueError` si un poids est négatif, si la somme des poids s'écarte de 1 de plus de 10⁻⁹, ou si une composante sort de [0, 1], signe qu'elle n'a pas été normalisée. Avec les poids (0,5 ; 0,3 ; 0,2), le souvenir « salaire » du scénario du crédit, de composantes 1, 0,9229 et 1, doit obtenir 0,97687.

```python
# [extrait] spécification
def score_pertinence(sim: float, rec: float, imp: float, poids: tuple[float, float, float]) -> float:
    """S = w_sim · sim + w_rec · rec + w_imp · imp ; refuse ce qui casse la borne [0, 1]."""
```

- Un poids négatif, ou une somme des poids qui s'écarte de 1 de plus de 10⁻⁹, lève `ValueError`. La tolérance est nécessaire : en flottant, 0,5 + 0,3 + 0,2 donne exactement 1, mais les poids (0,7 ; 0,29 ; 0,01) donnent 0,9999999999999999, et une comparaison stricte avec 1 les refuserait à tort.
- Une composante hors de [0, 1] lève `ValueError` : elle n'a pas été normalisée.

**Exemple chiffré.** `score_pertinence(1.0, 0.9229, 1.0, (0.5, 0.3, 0.2))` vaut 0,5 × 1 + 0,3 × 0,9229 + 0,2 × 1 = 0,5 + 0,27687 + 0,2 = 0,97687. C'est le score du souvenir « salaire » du scénario du crédit. Refus : (0,6 ; 0,6 ; −0,2) a un poids négatif, (0,5 ; 0,3 ; 0,3) a une somme de 1,1, et une similarité de 1,2 sort de [0, 1]. Tests : `TestScorePertinence`.

### Souvenir

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Souvenir.__post_init__()`** — Cette méthode doit jouer le rôle de l'archiviste qui, au moment où l'on dépose une fiche dans le classeur, vérifie que la note d'importance inscrite en haut est lisible : elle ne reçoit rien d'autre que le souvenir lui-même, que la dataclass vient de construire avec son texte, son jour de dernier accès et son importance, et doit lever `ValueError` si l'importance n'est pas un entier de 1 à 10. Elle ne renvoie rien ; la dataclass l'appelle automatiquement juste après son constructeur généré, si bien que `Souvenir("x", 0.0, 11)` échoue dès la construction, alors que le souvenir du salaire, d'importance 9, est accepté.

```python
# [extrait] spécification
@dataclass
class Souvenir:
    texte: str
    jour_acces: float
    importance: int

    def __post_init__(self) -> None:
        ...
```

- `texte` : ce dont on se souvient, tel qu'il ira dans le prompt.
- `jour_acces` : le jour du dernier accès, sur l'horloge simulée du palier 01 (`Horloge.jour()`). Il est modifié par `rappeler` lors de la relecture : la dataclass n'est donc pas gelée.
- `importance` : une note entière, de 1 (banal) à 10 (crucial), fixée à l'écriture du souvenir. Une valeur hors de 1 à 10 lève `ValueError` dès la construction, dans `__post_init__`, que la dataclass appelle juste après son `__init__` généré.

**Exemple.** `Souvenir("Salaire mensuel déclaré au dossier de crédit : 40 000 AED", 85.0, 9)` est un souvenir écrit, ou relu pour la dernière fois, au jour 85, et presque crucial. `Souvenir("x", 0.0, 11)` lève `ValueError`. Test : `TestRappeler.test_cas_limites_et_erreurs`.

### rappeler

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rappeler(question, souvenirs, plonger_texte, jour, k, demi_vie, poids)`** — Cette fonction doit être la bibliothécaire qui, devant la question d'un client, sort des rayonnages les quelques fiches qui méritent d'être posées sur le bureau du conseiller : elle reçoit la question, les souvenirs candidats, une fonction injectée qui plonge un texte en vecteur, le jour courant et son réglage, k = 2, une demi-vie de 30 jours et les poids (0,5 ; 0,3 ; 0,2). Elle lève `ValueError` si k est inférieur à 1, renvoie une liste vide s'il n'y a aucun souvenir, sinon calcule pour chacun la similarité, la récence et l'importance, les normalise, les combine en un score, trie du meilleur au moins bon en départageant les égalités par le texte, et renvoie les k premiers couples (score, souvenir). Les souvenirs gardés sont relus, leur jour d'accès passant au jour courant ; au jour 90, le client C-1 doit retrouver son salaire (0,9769) puis son crédit auto (0,8070).

```python
# [extrait] spécification
def rappeler(question: str, souvenirs: list[Souvenir], plonger_texte: Callable[[str], list[float]], jour: float,
             k: int = 2, demi_vie: float = 30.0,
             poids: tuple[float, float, float] = (0.5, 0.3, 0.2)) -> list[tuple[float, Souvenir]]:
    """Les k souvenirs les plus pertinents, avec leur score, du meilleur au moins bon."""
```

**Entrées.**

- `question` : le texte de la demande du client.
- `souvenirs` : les souvenirs candidats.
- `plonger_texte` : une fonction qui rend le vecteur d'un texte. La mémoire ne dépend d'aucun modèle d'embedding : on lui **injecte** cette fonction, comme on injecterait un bean `Function<String, List<Double>>` dans un service Spring. Dans les tests, c'est `VECTEURS.__getitem__`, la méthode d'accès d'un dictionnaire, l'équivalent d'une référence de méthode `vecteurs::get` en Java. Au palier 07, ce sera `recherche.plonger_texte`.
- `jour` : le jour courant, sur l'horloge simulée.
- `k`, `demi_vie` et `poids` : le réglage, avec les valeurs de l'étape 77.

**Comportement.**

1. `k < 1` lève `ValueError` ; une liste de souvenirs vide rend `[]`.
2. On plonge la question une seule fois, puis chaque souvenir. On calcule trois listes de composantes brutes : le cosinus question/souvenir, la récence de l'âge `jour - s.jour_acces`, et l'importance convertie en `float`. Chaque liste passe par `min_max`.
3. Pour chaque souvenir, le score est `score_pertinence(sims[j], recs[j], imps[j], poids)`.
4. On trie par score décroissant, en départageant les égalités par le texte, dans l'ordre alphabétique : deux exécutions donnent toujours le même ordre. On garde les k premiers couples `(score, souvenir)`.
5. Les souvenirs gardés sont **relus** : leur `jour_acces` passe à `jour`. Les autres ne bougent pas.

**Erreurs propagées.** Un souvenir dont `jour_acces` dépasse `jour` a un âge négatif, et `recence` lève `ValueError`. Un texte dont le vecteur est nul fait lever `ValueError` par `cosinus`. Aucune des deux erreurs n'est masquée.

**Exemple chiffré : le scénario du crédit de l'étape 77, recalculé à la main.** Au jour 90 de la relation, le client C-1 demande : « Hypothèque de 1 000 000 AED sur 25 ans : avec mon salaire et mon crédit, recevable ? Mensualité en USD ? ». Son plongement vaut q = [1, 1, 2, 1, 0, 1, 0, 0] (dette, revenu, crédit deux fois, durée, change). Sa mémoire compte quatre souvenirs :

| Souvenir | Vecteur | Jour d'accès | Importance |
|---|---|---|---|
| Salaire mensuel déclaré au dossier de crédit : 40 000 AED | [0, 1, 1, 0, 0, 0, 0, 0] | 85 | 9 |
| Crédit auto en cours : mensualité de 6 000 AED | [1, 0, 1, 0, 0, 0, 0, 0] | 60 | 8 |
| Cherchait un prêt personnel sur 48 mois | [0, 0, 1, 1, 0, 0, 0, 0] | 0 | 4 |
| A demandé le taux de change du dirham en USD | [0, 0, 0, 0, 0, 3, 0, 0] | 88 | 2 |

**Similarité.** Les trois premiers souvenirs ont chacun deux concepts communs avec q, dont le crédit, de poids 2 : q · v = 3, ‖v‖ = √2, cos = 3 / (√8 × √2) = 0,75. Le taux de change donne 1 / √8 ≈ 0,3536. Le min-max se fait avec lo = 0,3536 et hi = 0,75, et donne [1, 1, 1, 0].

**Récence.** Les âges valent 90 − 85 = 5, 90 − 60 = 30, 90 − 0 = 90 et 90 − 88 = 2 jours. Les récences valent 2^(−1/6) ≈ 0,8909, 2⁻¹ = 0,5, 2⁻³ = 0,125 et 2^(−1/15) ≈ 0,9548, car 2^(1/15) ≈ 1,0473. Le min-max se fait avec lo = 0,125 et hi = 0,9548, soit une étendue de 0,8298. Il donne (0,8909 − 0,125) / 0,8298 = 0,7659 / 0,8298 ≈ 0,9229, puis 0,375 / 0,8298 ≈ 0,4519, puis 0 et 1.

**Importance.** [9, 8, 4, 2] devient [1, 0,8571, 0,2857, 0], comme dans l'exemple de `min_max`.

**Scores**, avec les poids (0,5 ; 0,3 ; 0,2) :

- salaire : 0,5 × 1 + 0,3 × 0,9229 + 0,2 × 1 = 0,5 + 0,2769 + 0,2 = **0,9769** ;
- crédit auto : 0,5 × 1 + 0,3 × 0,4519 + 0,2 × 0,8571 = 0,5 + 0,1356 + 0,1714 = **0,8070** ;
- prêt personnel : 0,5 × 1 + 0,3 × 0 + 0,2 × 0,2857 = 0,5 + 0 + 0,0571 = 0,5571 ;
- taux de change : 0,5 × 0 + 0,3 × 1 + 0,2 × 0 = 0,3.

Avec k = 2, `rappeler` rend le salaire (0,9769) puis le crédit auto (0,8070), les deux souvenirs dont l'agent a besoin pour calculer le ratio d'endettement. Le taux de change, pourtant le plus récent, est dernier : il est hors sujet et banal. La relecture fait passer les jours d'accès de [85, 60, 0, 88] à [90, 90, 0, 88]. Tests : `TestRappeler.test_scenario_de_77`, `test_tous_les_scores` (k = 4) et `test_relire_remet_l_horloge_a_zero`.

### Ce qui change par rapport à l'étape 77

- **`cosinus` et `min_max` arrivent ici.** Dans l'étape 77, elles sont rangées avec les « fonctions canoniques » de la section 4. Dans les paliers, la mémoire est le premier composant qui en a besoin. Le palier 07 importera `cosinus` d'ici pour la recherche hybride, au lieu de le réécrire ; `min_max` ne sert qu'à la mémoire.
- **`rappeler` reçoit `plonger_texte` et `jour` en paramètres.** Dans l'étape 77, elle appelait `plonger(tokeniser(…))`, de la section RAG, et lisait l'horloge globale `HORLOGE.jour()`. Ici, le palier 06 ne dépend ni du palier 07, qui n'existe pas encore, ni d'une variable globale. Les tests lui passent un dictionnaire de vecteurs écrits à la main, et le palier 12 lui passera `recherche.plonger_texte` et `horloge.jour()`.
- **Trois gardes de plus.** L'importance hors de 1 à 10 est refusée par `Souvenir`, alors qu'elle n'était qu'un commentaire dans 77. Une liste vide donne `[]` dans `rappeler` et `ValueError` dans `min_max`. Et `k < 1` est refusé. Les nombres du scénario sont inchangés : 0,9769 et 0,8070.

## Squelette algorithmique

```text
ALGORITHME Cosinus
ENTRÉES : a, b, deux vecteurs de même dimension d
SORTIE  : cos(a, b) dans [−1, 1]
  SI longueur(a) ≠ longueur(b) ALORS ERREUR « dimensions différentes »
  na ← √(Σ aᵢ²) ; nb ← √(Σ bᵢ²)
  SI na = 0 OU nb = 0 ALORS ERREUR « vecteur nul »
  RETOURNER borner(Σ aᵢ bᵢ / (na × nb), −1, 1)

ALGORITHME MinMax
ENTRÉE  : x₁ … xₙ, n ≥ 1
SORTIE  : x̃₁ … x̃ₙ dans [0, 1]
  lo ← min des xᵢ ; hi ← max des xᵢ
  SI hi = lo ALORS RETOURNER [0, …, 0]
  RETOURNER [ (xⱼ − lo) / (hi − lo) POUR j DE 1 À n ]

ALGORITHME Récence
ENTRÉES : âge ≥ 0, demi-vie > 0
SORTIE  : rec dans ]0, 1]
  λ ← ln 2 / demi-vie
  RETOURNER e^(−λ × âge)

ALGORITHME ScorePertinence
ENTRÉES : sim, rec, imp dans [0, 1] ; poids (w₁, w₂, w₃) ≥ 0 de somme 1
SORTIE  : S dans [0, 1]
  SI un poids < 0 OU |w₁ + w₂ + w₃ − 1| > 10⁻⁹ ALORS ERREUR
  SI une composante est hors de [0, 1] ALORS ERREUR « normaliser d'abord »
  RETOURNER w₁ × sim + w₂ × rec + w₃ × imp

ALGORITHME Rappeler
ENTRÉES : question, souvenirs s₁ … sₙ, plonger (texte → vecteur), jour, k ≥ 1, demi-vie, poids
SORTIE  : les k couples (score, souvenir) de plus grand score, du meilleur au moins bon
  SI k < 1 ALORS ERREUR
  SI n = 0 ALORS RETOURNER liste vide
  vq ← plonger(question)                                              (une seule fois)
  sims ← MinMax([ Cosinus(vq, plonger(sⱼ.texte)) POUR CHAQUE j ])
  recs ← MinMax([ Récence(jour − sⱼ.jour d'accès, demi-vie) POUR CHAQUE j ])
  imps ← MinMax([ sⱼ.importance POUR CHAQUE j ])
  notes ← [ (ScorePertinence(sims[j], recs[j], imps[j], poids), sⱼ) POUR CHAQUE j ]
  gardés ← les k premiers de notes, triées par score décroissant puis par texte croissant
  POUR CHAQUE (score, s) DANS gardés FAIRE  s.jour d'accès ← jour  FIN POUR    (relecture)
  RETOURNER gardés
```

**Complexité.** Pour n souvenirs de dimension d, `rappeler` fait n + 1 appels à la fonction de plongement, puis n cosinus en O(d) chacun, soit O(n × d). Les récences, les trois min-max et les n scores coûtent O(n), et le tri O(n log n). La mémoire occupée est O(n) pour les trois listes et les notes. En production, on ne calcule pas ce score sur toute la mémoire : une base vectorielle présélectionne d'abord une cinquantaine de candidats, et le score ne départage que ceux-là (étape 17). Le min-max dépend de l'ensemble des candidats : ajouter ou retirer un souvenir peut changer le score des autres, mais jamais l'ordre d'une composante prise seule.

**Du squelette au code.** `Cosinus` est `cosinus`, avec `math.sqrt` pour les normes et `max(-1.0, min(1.0, …))` pour la borne. `MinMax` est `min_max`. `Récence` est `recence`, avec `math.log(2)` et `math.exp`. `ScorePertinence` est `score_pertinence`. `Rappeler` est `rappeler` : la fonction `plonger` est le paramètre `plonger_texte`, le tri est `sorted` avec la clé `(-score, texte)`, et la relecture est l'affectation de `s.jour_acces`. Un souvenir est un objet `Souvenir`, dont l'importance est contrôlée dans `__post_init__`.

## Cas d'usage aux Émirats

Les vecteurs sont écrits à la main sur quelques concepts, et les montants sont illustratifs. Les règles citées, comme le plafond d'endettement de 30 % pour un retraité, sont celles du parcours et sont à confirmer avec le texte en vigueur.

### Immobilier — l'acheteur qui a changé de projet

L'agence A-3, à Dubaï, suit l'acheteur C-7 depuis trois mois. Au jour 90, il demande une villa avec jardin, près d'une bonne école. Sa question se plonge en (0,8 ; 0 ; 0 ; 0,6 ; 0), sur cinq axes : villa et jardin, appartement et Marina, budget, famille et école, contact. Sa mémoire contient cinq souvenirs, avec ces âges et ces importances : « cherche une villa avec jardin » (0 jour, 8), « budget maximum 3,5 M AED » (15 jours, 9), « deux enfants scolarisés » (30 jours, 6), « cherchait un deux-pièces à Dubai Marina » (90 jours, 9) et « préfère être appelé le soir » (60 jours, 3). Avec les réglages par défaut et k = 3, `rappeler` donne 0,9667 à la villa, 0,6996 au budget et 0,6036 aux enfants, et laisse dehors le vieux projet Marina (0,3400) et la préférence d'horaire (0,0429). Ce sont les nombres de l'étape 17. Sans normalisation, avec l'importance brute de 1 à 10, le projet Marina abandonné aurait pris la place des enfants, avec 1,9495 contre 1,65 : l'agent aurait proposé des appartements à un client qui cherche une villa.

### Banque — une contrainte ancienne mais critique

La banque B-1 suit le client C-4, retraité. Au jour 200, il demande un nouveau prêt personnel. On plonge sur cinq axes (dette, revenu, crédit, durée, contact) : la question vaut (1 ; 1 ; 2 ; 1 ; 0). Quatre souvenirs sont candidats :

- « client retraité : plafond d'endettement 30 % », écrit il y a 180 jours, importance 10, vecteur (2 ; 1 ; 1 ; 0 ; 0) ;
- « préfère être contacté en arabe », 5 jours, importance 3 ;
- « a demandé les horaires de l'agence A-3 », 2 jours, importance 1 ;
- « prêt auto soldé en janvier », 50 jours, importance 6, vecteur (0 ; 0 ; 1 ; 1 ; 0).

Les cosinus valent 5 / √42 ≈ 0,7715 pour le plafond, 3 / √14 ≈ 0,8018 pour le prêt soldé, et 0 pour les deux souvenirs de contact. La récence du plafond est minuscule, 2⁻⁶ ≈ 0,0156. Avec les poids par défaut (0,5 ; 0,3 ; 0,2), le prêt soldé obtient 0,7067 et le plafond 0,6811 : le plafond entre dans le top 2, porté par sa similarité et son importance. Si une équipe règle les poids sur (0,2 ; 0,6 ; 0,2) pour « privilégier le récent », le plafond tombe à 0,3925, quatrième, derrière la langue de contact (0,6036) et les horaires (0,6000). L'agent appliquerait alors le plafond général de 50 % à un retraité. Le réglage des poids est une décision métier, qui se valide sur des cas de référence (palier 10), pas une préférence de développeur.

### RH — un souvenir venu du futur

Un cabinet RH multi-émirats synchronise la mémoire de son agent depuis deux serveurs. L'un d'eux horodate en temps universel, et un souvenir sur le statut d'un dossier de fin de service arrive avec le jour d'accès 90,2, alors que l'horloge de l'agent indique le jour 90,0. Son âge vaut −0,2 jour, et `recence` lève `ValueError`. Sans cette garde, sa récence vaudrait 2^(0,2/30) ≈ 1,0046, plus que 1. Le min-max la ramènerait en silence à 1, la plus haute de toutes : le souvenir mal daté passerait en tête du classement, et personne ne verrait le décalage d'horloge. L'erreur visible force à corriger la synchronisation, au lieu de laisser un défaut d'infrastructure fausser le prompt.

## Travail à faire

1. Ouvre un terminal PowerShell dans le dossier `projet/` du palier, puis vérifie que les tests des paliers 01 à 05 passent et que les 13 tests du palier 06 échouent tous par `NotImplementedError` :

   ```text
   cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\06-Memoire\projet"
   python -m unittest -v
   ```

   Si `python` ouvre le Microsoft Store, utilise le chemin complet de l'interpréteur : `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m unittest -v`.

2. Lis `tests/test_06_memoire.py`. Le dictionnaire `VECTEURS` donne le plongement de chaque texte, et `souvenirs()` fabrique les quatre souvenirs du scénario du crédit, avec des textes courts.

3. Ouvre `agent/memoire.py`. Code les fonctions dans l'ordre, en lançant leur classe de tests après chacune :

   ```text
   python -m unittest -v tests.test_06_memoire.TestCosinus
   python -m unittest -v tests.test_06_memoire.TestMinMax
   python -m unittest -v tests.test_06_memoire.TestRecence
   python -m unittest -v tests.test_06_memoire.TestScorePertinence
   ```

4. Code `Souvenir.__post_init__`, puis `rappeler`, et lance :

   ```text
   python -m unittest -v tests.test_06_memoire.TestRappeler
   ```

5. Lance tous les tests, puis la démo :

   ```text
   python -m unittest -v
   python demo.py
   ```

## Critères de réussite

- `python -m unittest -v`, lancé depuis `projet/`, affiche `OK` pour 82 tests : les 69 des paliers 01 à 05 et les 13 du palier 06.
- `python demo.py` affiche exactement la sortie ci-dessous, et sa dernière ligne est `OK — palier 06 terminé.`
- Tu sais refaire à la main, sur une feuille A4, les scores 0,9769 et 0,8070 du scénario du crédit, et dire pourquoi on normalise avant de pondérer.

### Sortie attendue de demo.py

```text
Palier 06 — la mémoire du client C-1, au jour 90 de la relation
1. Composantes brutes, puis ramenées dans [0, 1] par min-max :
   cosinus  0.7500  0.7500  0.7500  0.3536   →  1.0000  1.0000  1.0000  0.0000
   récence  0.8909  0.5000  0.1250  0.9548   →  0.9229  0.4519  0.0000  1.0000
   importance 9  8  4  2   →  1.0000  0.8571  0.2857  0.0000
2. Score de pertinence S = 0.5 sim + 0.3 rec + 0.2 imp, tous les souvenirs :
   0.9769  Salaire mensuel déclaré au dossier de crédit : 40 000 AED
   0.8070  Crédit auto en cours : mensualité de 6 000 AED
   0.5571  Cherchait un prêt personnel sur 48 mois
   0.3000  A demandé le taux de change du dirham en USD
3. Les 2 souvenirs mis dans le prompt : [0.9769, 0.807]
   relus, leurs jours d'accès deviennent : [90.0, 90.0, 0.0, 88.0]
4. Demi-vie 30 jours : un souvenir de 90 jours pèse 0.125 de sa valeur neuve
OK — palier 06 terminé.
```

## Pour aller plus loin

1. **Un seul souvenir.** Que rend `rappeler` avec un seul souvenir, quel que soit son texte ? Réponse : le souvenir avec le score 0,0, parce que le min-max d'une seule valeur vaut 0 pour les trois composantes. `rappeler` classe, il ne filtre pas : pour écarter un souvenir hors sujet, il faut ajouter un seuil sur le cosinus brut.
2. **Une demi-vie d'une semaine.** Sur le scénario du crédit, passe `demi_vie=7.0`. Réponse : le salaire et le crédit auto restent en tête, mais le score du crédit auto tombe de 0,8070 à 0,6901, parce que son âge de 30 jours vaut maintenant plus de quatre demi-vies, et sa récence normalisée tombe à 0,0624.
3. **La même question le lendemain.** Après le rappel du jour 90, qui a relu le salaire et le crédit auto, rappelle de nouveau la même question au jour 91, avec k = 4. Réponse : le salaire obtient 1,0 et le crédit auto 0,9714, car les deux souvenirs relus ont le même âge d'un jour et la récence maximale ; le taux de change tombe à 0,2845.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`. Chaque fichier montre un bloc de la solution, l'explique ligne par ligne et dit quel test passe :

- [01 — Le cosinus](<solutions/progression/01-Le-cosinus.md>) : produit scalaire, normes, refus du vecteur nul, borne à [−1, 1].
- [02 — La normalisation min-max](<solutions/progression/02-La-normalisation-min-max.md>) : la formule, la liste vide et le signal constant.
- [03 — La récence](<solutions/progression/03-La-recence.md>) : λ à partir de la demi-vie, l'exponentielle et les âges invalides.
- [04 — Le score de pertinence](<solutions/progression/04-Le-score-de-pertinence.md>) : les gardes qui protègent la borne [0, 1], et la somme pondérée.
- [05 — Le souvenir](<solutions/progression/05-Le-souvenir.md>) : la `dataclass` et son contrôle dans `__post_init__`.
- [06 — Rappeler](<solutions/progression/06-Rappeler.md>) : le plongement injecté, les trois composantes, le tri déterministe et la relecture.
- [07 — Assemblage, tests et démo](<solutions/progression/07-Assemblage-tests-et-demo.md>) : le module complet, tous les tests, la démo et le passage au palier 07.

La solution entière est dans `solutions/agent/memoire.py`. Ses tests et sa démo sont dans `solutions/tests/` et `solutions/demo.py`.
