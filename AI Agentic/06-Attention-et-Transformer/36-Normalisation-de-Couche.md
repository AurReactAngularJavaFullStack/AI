# Étape 36 — Layer Normalization — Stabilisation de l'Entraînement

> Étape 36 du parcours · Prérequis : [Encodage de position](<35-Encodage-de-Position.md>) · Suite : [Mélange d'experts (MoE)](<36b-Melange-d-Experts-MoE.md>)

## Définition

La normalisation de couche (LayerNorm) recentre et remet à l'échelle les activations d'**un seul token**, en calculant la moyenne μ et la variance σ² sur ses d coordonnées, sans jamais regarder les autres tokens ni les autres phrases du lot. Le vecteur normalisé x̂ a une moyenne nulle et une variance presque égale à 1. Deux vecteurs appris, γ (gain) et β (décalage), permettent ensuite au modèle de redonner aux activations l'échelle et le centre dont il a besoin. La variante RMSNorm saute le recentrage : elle divise seulement par la racine de la moyenne des carrés et n'a pas de β. Ces normalisations stabilisent l'entraînement des Transformers profonds, parce qu'elles empêchent l'échelle des activations de dériver d'une couche à l'autre.

## Rôle dans un agent

La normalisation s'exécute dans chaque couche du LLM, avant ou après l'attention et le bloc feed-forward, pendant l'étape **décider** de la boucle percevoir → décider → agir → observer. Le développeur d'agent la rencontre dans trois situations concrètes. Quand il porte ou réimplémente un modèle, la moindre différence (diviseur d au lieu de d − 1, valeur de ε, présence de β) change toutes les sorties. Quand il entraîne un petit modèle maison sur des données numériques (montants, prix, journaux), les invariances de LayerNorm décident de ce que le modèle peut encore voir. Et quand une entrée dégénérée arrive en production (un token constant, une fenêtre sans activité), c'est ε qui sépare un résultat défini d'un NaN silencieux.

## Équation complète

Moyenne des d coordonnées du token :

$$
\mu = \frac{1}{d} \sum_{i=1}^{d} x_i
$$

Variance, avec le diviseur d :

$$
\sigma^2 = \frac{1}{d} \sum_{i=1}^{d} (x_i - \mu)^2
$$

Vecteur normalisé :

$$
\hat{x}_i = \frac{x_i - \mu}{\sqrt{\sigma^2 + \epsilon}}
$$

Sortie, avec le gain et le décalage appris :

$$
y_i = \gamma_i \, \hat{x}_i + \beta_i
$$

Variante RMSNorm, sans recentrage ni β :

$$
\text{RMSNorm}(x)_i = \frac{x_i}{\sqrt{\frac{1}{d} \sum_{j=1}^{d} x_j^2 + \epsilon}} \, \gamma_i
$$

## Décryptage des symboles

$$
x
$$

Le vecteur des activations d'un seul token : d nombres réels, quelconques ; variable Python `x`.

$$
d
$$

Le nombre de coordonnées du token, la largeur du modèle (notée d_model aux étapes 33 et 34) : un entier ≥ 1 ; c'est `len(x)`.

$$
\mu
$$

La moyenne des d coordonnées du token : un réel ; fonction `moyenne(x)`.

$$
\sigma^2
$$

La variance des coordonnées autour de μ, avec le diviseur d (et non d − 1) : un réel ≥ 0 ; fonction `variance(x)`.

$$
\epsilon
$$

Une petite constante positive, souvent 10⁻⁵ ou 10⁻⁶, qui garde le dénominateur strictement positif : un réel ≥ 0 ; paramètre `eps`.

$$
\hat{x}
$$

Le vecteur normalisé, de moyenne 0 et de variance σ² / (σ² + ε), donc presque 1 : d réels ; résultat de `layer_norm(x)` avec γ = 1 et β = 0.

$$
\gamma
$$

Le gain appris, un nombre par coordonnée, qui vaut 1 au départ de l'entraînement : un vecteur de d réels ; paramètre `gamma`.

$$
\beta
$$

Le décalage appris, un nombre par coordonnée, qui vaut 0 au départ de l'entraînement : un vecteur de d réels ; paramètre `beta`.

$$
y
$$

La sortie de la couche de normalisation, γ ⊙ x̂ + β, où ⊙ désigne le produit coordonnée par coordonnée : d réels ; valeur renvoyée par `layer_norm`.

$$
\text{RMS}(x)
$$

La racine de la moyenne des carrés des coordonnées, √((1/d) ∑ xⱼ² + ε), qui sert de dénominateur à RMSNorm : un réel > 0 ; calculée dans `rms_norm(x)`.

L'ancienne version écrivait ces symboles avec des délimiteurs `\(…\)` que l'aperçu n'affichait pas ; ils sont désormais définis un par un.

## Démonstration

### 1. Le vecteur normalisé a une moyenne nulle

On fait la moyenne des x̂ᵢ. Le dénominateur √(σ² + ε) ne dépend pas de i, donc il sort de la somme :

$$
\frac{1}{d} \sum_{i=1}^{d} \hat{x}_i = \frac{1}{\sqrt{\sigma^2 + \epsilon}} \cdot \frac{1}{d} \sum_{i=1}^{d} (x_i - \mu) = \frac{1}{\sqrt{\sigma^2 + \epsilon}} \, (\mu - \mu) = 0
$$

La deuxième égalité tient parce que (1/d) ∑ xᵢ = μ par définition, et que (1/d) ∑ μ = μ. Le résultat vaut pour tout ε ≥ 0.

### 2. Sa variance vaut σ² / (σ² + ε), donc presque 1

Comme la moyenne de x̂ est nulle, sa variance est la moyenne de ses carrés :

$$
\frac{1}{d} \sum_{i=1}^{d} \hat{x}_i^2 = \frac{1}{\sigma^2 + \epsilon} \cdot \frac{1}{d} \sum_{i=1}^{d} (x_i - \mu)^2 = \frac{\sigma^2}{\sigma^2 + \epsilon}
$$

La dernière égalité tient parce que la somme qui reste est exactement la définition de σ². La variance de x̂ vaut donc 1 si ε = 0, et un peu moins de 1 sinon : pour x = [2, 0, 4, 2], σ² = 2 et la variance de x̂ vaut 2 / 2,00001 ≈ 0,999995. On en déduit aussi la norme : ‖x̂‖² = d · σ² / (σ² + ε) ≈ d. Quelle que soit l'échelle d'entrée, un token normalisé a une norme proche de √d ; ici ‖x̂‖² vaut 3,99998 pour d = 4.

### 3. LayerNorm est invariant par changement d'échelle positif et par décalage commun

On remplace chaque coordonnée xᵢ par a·xᵢ + b, avec a > 0 et le même b pour toutes les coordonnées. La moyenne devient a·μ + b, parce que la moyenne est linéaire ; la variance devient a²·σ², parce que b disparaît dans les écarts à la moyenne et que chaque écart est multiplié par a. Le vecteur normalisé devient :

$$
\frac{a x_i + b - (a \mu + b)}{\sqrt{a^2 \sigma^2 + \epsilon}} = \frac{a (x_i - \mu)}{a \sqrt{\sigma^2 + \epsilon / a^2}} = \frac{x_i - \mu}{\sqrt{\sigma^2 + \epsilon / a^2}}
$$

La deuxième égalité tient parce que √(a²) = a quand a > 0. Si ε = 0, on retrouve exactement x̂ : LayerNorm(a·x + b) = LayerNorm(x). Si ε > 0, la seule différence est ε / a² au lieu de ε : pour a = 3 et b = 5 sur l'exemple, l'écart maximal vaut 3,1 × 10⁻⁶. Si a < 0, √(a²) = −a et le signe s'inverse ; pour a = −1, on a a² = 1, donc LayerNorm(−x) = −LayerNorm(x) exactement, même avec ε. Conséquence pratique : après LayerNorm, un vecteur ne garde **ni son niveau ni son échelle**, seulement sa forme.

### 4. RMSNorm n'est invariant qu'à l'échelle

RMSNorm ne soustrait pas la moyenne. Pour a > 0, la moyenne des carrés de a·x vaut a² fois celle de x, donc RMS(a·x) = a · RMS(x) quand ε = 0, et RMSNorm(a·x) = RMSNorm(x). Un décalage commun, lui, change le résultat. Contre-exemple chiffré : RMSNorm([2, 0, 4, 2]) divise par √((4 + 0 + 16 + 4) / 4) = √6 ≈ 2,44949 et donne [0,8165 ; 0 ; 1,633 ; 0,8165] ; RMSNorm([3, 1, 5, 3]) divise par √11 et donne [0,9045 ; 0,3015 ; 1,5076 ; 0,9045]. Enfin, sur un vecteur déjà centré, la moyenne des carrés est exactement σ², donc RMSNorm(x − μ) = LayerNorm(x) : RMSNorm est LayerNorm sans le recentrage.

L'ancienne version affirmait que les modèles à RMSNorm, comme Llama, « apprennent le recentrage ailleurs, dans les biais des couches linéaires ». C'est faux pour Llama, dont les couches linéaires n'ont pas de biais. Ces modèles ne recentrent tout simplement pas : l'article qui a introduit RMSNorm (Zhang et Sennrich, 2019) a constaté que l'invariance au recentrage n'était pas nécessaire dans ses expériences, et RMSNorm économise le calcul de la moyenne.

### 5. Sans ε, un token constant donne 0/0, et non un infini

Si toutes les coordonnées sont égales, chaque écart xᵢ − μ vaut 0 et σ² = 0. Sans ε, x̂ᵢ = 0 / √0 = 0/0, une forme indéterminée. L'ancienne version disait que « le token disparaîtrait dans un infini » ; c'est inexact. En arithmétique flottante IEEE 754, celle de NumPy et de PyTorch, 0/0 donne NaN (« not a number »), et ce NaN se propage à tout ce qui en dépend. En Python pur, la division lève `ZeroDivisionError` ; la fonction de ce fichier lève une `ValueError` explicite. Avec ε > 0, le calcul devient 0 / √ε = 0, donc x̂ = 0 et la sortie vaut exactement β : le résultat est défini. Le NaN est dangereux parce qu'il est silencieux : toute comparaison avec NaN est fausse, si bien qu'un score NaN ne franchit **aucun** seuil, ni « > 0,9 » ni « ≤ 0,9 ».

### 6. Pourquoi normaliser : l'échelle dérive de couche en couche

Une couche qui multiplierait toutes les coordonnées par 3 multiplierait la norme par 3¹⁰ = 59 049 après 10 couches, et les produits scalaires de l'attention par 3²⁰ ≈ 3,5 × 10⁹ : la softmax saturerait et le gradient s'éteindrait (étape 32). Une LayerNorm entre les couches ramène la norme au carré à environ d (point 2), quelle que soit la dérive : le programme retrouve 4,0000 après les 10 multiplications.

### 7. LayerNorm contre BatchNorm

BatchNorm normalise chaque coordonnée **à travers les tokens du lot**. Pendant l'entraînement, la sortie d'un token dépend donc de ses voisins de lot : le programme normalise x = [2, 0, 4, 2] avec un voisin nul, puis avec un voisin [10, 10, 10, 10], et obtient [1 ; 0 ; 1 ; 1] puis [−1 ; −1 ; −1 ; −1]. L'ancienne version ajoutait qu'à l'inférence, avec une seule phrase, la moyenne de BatchNorm « ne voudrait plus rien dire » : en réalité, BatchNorm n'utilise pas la phrase seule à l'inférence, mais des statistiques courantes (moyennes mobiles de la moyenne et de la variance) accumulées pendant l'entraînement. Ses vrais défauts pour un Transformer sont ailleurs : l'écart entre statistiques d'entraînement et d'inférence, la dépendance à la composition des lots pendant l'entraînement, et les séquences de longueurs variables. LayerNorm ne regarde que les coordonnées du token en cours : elle calcule la même chose à l'entraînement et en production.

### 8. Exemple fait à la main (le code reprend ces nombres)

On prend un token x = [2, 0, 4, 2] et ε = 10⁻⁵.

- Moyenne : (2 + 0 + 4 + 2) / 4 = 2.
- Écarts à 2 : 0, −2, 2, 0 ; carrés : 0, 4, 4, 0 ; variance : 8 / 4 = 2.
- Dénominateur : √(2 + 10⁻⁵) ≈ 1,414217 ; x̂ ≈ [0 ; −1,41421 ; 1,41421 ; 0].
- Avec le diviseur d − 1, celui de `statistics.variance` et de PyTorch par défaut, la variance vaudrait 8 / 3 ≈ 2,6667 et x̂ ≈ [0 ; −1,2247 ; 1,2247 ; 0] : ce ne serait plus la formule.
- Avec γ = 2 et β = 1 : y = 2x̂ + 1 ≈ [1 ; −1,8284 ; 3,8284 ; 1].
- RMSNorm : moyenne des carrés (4 + 0 + 16 + 4) / 4 = 6, division par √6 : [0,8165 ; 0 ; 1,633 ; 0,8165].

## Effets et comportement

- **L'échelle est remise à zéro à chaque couche.** La norme d'un token normalisé reste proche de √d, ce qui protège la softmax de la saturation.
- **Le niveau et l'échelle d'entrée sont effacés.** Deux tokens qui ne diffèrent que par un facteur positif et un décalage commun donnent la même sortie (point 3) ; seuls γ et β réintroduisent une échelle, la même pour tous les tokens.
- **ε ne compte que pour les tokens presque constants.** Pour [2, 0, 4, 2], passer de ε = 10⁻⁵ à 10⁻⁶ change la sortie de moins de 10⁻⁵ ; pour un token presque constant, la même modification peut changer une coordonnée de 0,3086 à 0,8165.
- **RMSNorm est plus simple et plus rapide.** Elle garde l'invariance d'échelle, perd l'invariance au décalage, et n'a pas de β.
- **Indispensable en pratique.** Toutes les architectures Transformer profondes utilisent une normalisation de ce type ; sans elle, l'entraînement de dizaines de couches devient instable.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| μ | `moyenne(x)` |
| σ² (diviseur d) | `variance(x)` |
| x̂, puis γ ⊙ x̂ + β | `layer_norm(x, gamma, beta, eps)` |
| RMSNorm(x) | `rms_norm(x, gamma, eps)` |
| BatchNorm, pour comparaison | `batch_norm_entrainement(lot, eps)` |
| ε | `eps` |

### Déroulé, ligne par ligne

**`moyenne(x)`** refuse un vecteur vide (`ValueError`), puis renvoie `sum(x) / len(x)` : 2,0 pour `[2.0, 0.0, 4.0, 2.0]`.

**`variance(x)`** renvoie `sum((v - mu) ** 2 for v in x) / len(x)` : le diviseur est `len(x)`, c'est-à-dire d, comme dans la formule. Pour l'exemple, les carrés des écarts valent 0, 4, 4 et 0, et la fonction renvoie 2,0. Le module `statistics` de Python propose les deux versions : `statistics.pvariance` divise par d (2,0), `statistics.variance` par d − 1 (2,6667).

**`layer_norm(x, gamma, beta, eps)`**.

- `gamma` et `beta` valent par défaut `[1.0] * d` et `[0.0] * d`, leurs valeurs de départ à l'entraînement : la sortie est alors x̂.
- La garde refuse un vecteur vide, des γ ou β de mauvaise taille et un ε négatif.
- `if var + eps == 0` : variance nulle et ε nul donneraient 0/0 ; on lève une `ValueError` au lieu de laisser passer un NaN (point 5).
- `ecart = math.sqrt(var + eps)` vaut 1,414217 pour l'exemple ; la compréhension renvoie `g * (v - mu) / ecart + b` pour chaque coordonnée, soit `[0.0, -1.41421, 1.41421, 0.0]`.

**`rms_norm(x, gamma, eps)`**. `carre_moyen` vaut `(4 + 0 + 16 + 4) / 4 = 6.0` ; `rms = math.sqrt(6.0 + 1e-5)` ; chaque coordonnée est divisée par `rms` et multipliée par son γ. Il n'y a ni moyenne soustraite, ni β.

**`batch_norm_entrainement(lot, eps)`**. `zip(*lot)` regroupe la même coordonnée de tous les tokens du lot ; chaque colonne reçoit sa moyenne et sa variance, et chaque token est normalisé avec les statistiques **de la colonne**, donc de ses voisins. C'est le comportement de BatchNorm à l'entraînement ; la fonction ne sert qu'à la comparaison du point 7.

**`arrondir(v, n)`** arrondit pour l'affichage ; le `+ 0.0` transforme un éventuel `-0.0` en `0.0`.

**`main()`**, bloc par bloc.

1. μ = 2, σ² = 2, x̂ = `[0.0, -1.41421, 1.41421, 0.0]` ; la moyenne de x̂ vaut 0 et sa variance 0,999995, soit 2 / (2 + 10⁻⁵) (points 1, 2 et 8). Puis la version fautive au diviseur d − 1 : `[0.0, -1.2247, 1.2247, 0.0]`.
2. Avec γ = 2 et β = 1, chaque coordonnée vaut exactement 2x̂ + 1.
3. LayerNorm(3x + 5) diffère de LayerNorm(x) de 3,1 × 10⁻⁶ avec ε, de moins de 10⁻¹⁵ avec ε = 0 ; LayerNorm(−x) = −LayerNorm(x) ; ‖x̂‖² vaut 3,99998 (point 3).
4. RMSNorm(x), RMSNorm(x + 1), puis les deux `assert` : RMSNorm(3x) = RMSNorm(x) et RMSNorm(x − μ) = LayerNorm(x) (point 4).
5. Le token constant donne `[0.0, 0.0, 0.0, 0.0]` avec ε, et exactement β avec β = 0,5 ; sans ε, `ValueError`. Le dernier `assert` vérifie qu'un NaN n'est ni supérieur à 0,9 ni inférieur ou égal (point 5).
6. Dix multiplications par 3 : la norme est multipliée par 59 049, les produits scalaires par 3 486 784 401 ; après LayerNorm, ‖x̂‖² revient à 4 (point 6).
7. BatchNorm donne `[1.0, 0.0, 1.0, 1.0]` ou `[-1.0, -1.0, -1.0, -1.0]` selon le voisin ; LayerNorm(x) ne change pas (point 7).
8. Les nombres des cas d'usage : trois séries de prix (doublée, décalée de 200, convertie en USD) donnent exactement la même normalisation que la série d'origine ; un token presque constant donne 0,3086 avec ε = 10⁻⁵ et 0,8165 avec ε = 10⁻⁶.
9. Un vecteur vide et un γ de mauvaise taille lèvent `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`moyenne(x)`** — Cette fonction est le niveau à bulle de l'atelier, celui qui dit où se trouve le milieu d'une rangée de mesures : elle reçoit la liste x des d coordonnées d'un token, lève une `ValueError` si la liste est vide, puisqu'on ne peut pas diviser par zéro, puis additionne toutes les coordonnées et divise par leur nombre. Elle renvoie μ, soit 2,0 pour `[2.0, 0.0, 4.0, 2.0]` ; `variance`, `layer_norm`, `batch_norm_entrainement` et les `assert` de `main` s'appuient sur elle, par exemple pour vérifier que la moyenne de x̂ est nulle à 10⁻¹⁵ près.

**`layer_norm(x, gamma, beta, eps)`** — C'est le tailleur qui remet chaque token à la même mesure avant de le laisser repartir : la fonction reçoit le vecteur x d'un token, les vecteurs γ et β, qui valent par défaut des 1 et des 0, et ε, qui vaut 10⁻⁵ par défaut. Elle lève une `ValueError` pour un vecteur vide, un γ ou un β de mauvaise taille, un ε négatif, ou une variance nulle avec ε nul, qui donnerait 0/0 ; sinon, elle retranche la moyenne à chaque coordonnée, divise par √(σ² + ε), multiplie par γ et ajoute β. Elle renvoie le vecteur normalisé, `[0.0, -1.41421, 1.41421, 0.0]` pour l'exemple, et `[1.0, -1.8284, 3.8284, 1.0]` avec γ = 2 et β = 1.

**`rms_norm(x, gamma, eps)`** — Voici le tailleur pressé, qui ajuste la taille sans recentrer le vêtement : la fonction reçoit le vecteur x, le vecteur γ, des 1 par défaut, et ε, 10⁻⁵ par défaut, refuse par une `ValueError` les mêmes entrées invalides que `layer_norm` ainsi qu'un vecteur nul avec ε nul, puis calcule la moyenne des carrés des coordonnées, en prend la racine après ajout de ε, et divise chaque coordonnée par ce nombre avant de la multiplier par son γ. Elle renvoie `[0.8165, 0.0, 1.633, 0.8165]` pour l'exemple, soit une division par √6 ; `main` montre qu'elle ignore une multiplication par 3 mais pas un décalage de 1, et qu'elle redonne LayerNorm quand on lui passe le vecteur déjà centré.

**`ecart_max(u, v)`** — Cette petite fonction est le contrôleur qui pose deux pièces l'une sur l'autre et cherche l'endroit où elles diffèrent le plus : elle reçoit deux vecteurs u et v, calcule la valeur absolue de la différence coordonnée par coordonnée et renvoie la plus grande. `main` l'utilise comme juge des invariances : LayerNorm(3x + 5) ne s'écarte de LayerNorm(x) que de 3,1 × 10⁻⁶, à cause du seul ε, alors que BatchNorm donne au même token des sorties qui s'écartent de plus de 0,5 selon son voisin de lot.

**`arrondir(v, n)`** — Ce petit utilitaire est le greffier qui recopie les résultats au propre : il reçoit une liste de flottants et un nombre n de décimales, 4 par défaut, arrondit chaque valeur à n chiffres après la virgule et lui ajoute `0.0`, ce qui transforme un éventuel `-0.0` en `0.0` pour que l'affichage et les comparaisons ne soient pas troublés par un signe moins sans objet. Il renvoie la liste ainsi nettoyée, et `main` s'en sert pour comparer les sorties aux valeurs attendues, comme `[0.0, -1.2247, 1.2247, 0.0]` pour la version fautive au diviseur d − 1.

**`main()`** — Le chef d'orchestre déroule les neuf tableaux du fichier sur le token x = `[2.0, 0.0, 4.0, 2.0]` : il calcule μ, σ² et x̂, montre l'erreur du diviseur d − 1, vérifie le rôle de γ et β, les invariances de LayerNorm, puis celles de RMSNorm, avant d'examiner le token constant `[3.0, 3.0, 3.0, 3.0]`, qui donne des zéros avec ε et une `ValueError` sans lui. Il fait ensuite exploser l'échelle par dix multiplications par 3, oppose BatchNorm à LayerNorm, vérifie les nombres des cas d'usage, dont 0,3086 et 0,8165 pour un token presque constant, et contrôle deux entrées invalides ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 36 — LayerNorm et RMSNorm en Python pur : moyenne, variance, invariances, epsilon."""
import math
import statistics
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def moyenne(x: list[float]) -> float:
    if not x:
        raise ValueError("vecteur vide")
    return sum(x) / len(x)


def variance(x: list[float]) -> float:
    """σ² = (1/d) Σ (x_i − μ)² : diviseur d, comme dans la formule (pas d − 1)."""
    mu = moyenne(x)
    return sum((v - mu) ** 2 for v in x) / len(x)


def layer_norm(x: list[float], gamma: list[float] | None = None, beta: list[float] | None = None,
               eps: float = 1e-5) -> list[float]:
    """y_i = γ_i (x_i − μ) / √(σ² + ε) + β_i, sur les d coordonnées d'UN token."""
    d = len(x)
    gamma = [1.0] * d if gamma is None else gamma
    beta = [0.0] * d if beta is None else beta
    if d == 0 or len(gamma) != d or len(beta) != d or eps < 0:
        raise ValueError("il faut un vecteur non vide, γ et β de même taille, et ε >= 0")
    mu, var = moyenne(x), variance(x)
    if var + eps == 0:
        raise ValueError("variance nulle et ε = 0 : (x − μ)/σ vaut 0/0, la normalisation n'est pas définie")
    ecart = math.sqrt(var + eps)
    return [g * (v - mu) / ecart + b for v, g, b in zip(x, gamma, beta)]


def rms_norm(x: list[float], gamma: list[float] | None = None, eps: float = 1e-5) -> list[float]:
    """y_i = γ_i x_i / √((1/d) Σ x_j² + ε) : ni soustraction de la moyenne, ni β."""
    d = len(x)
    gamma = [1.0] * d if gamma is None else gamma
    if d == 0 or len(gamma) != d or eps < 0:
        raise ValueError("il faut un vecteur non vide, γ de même taille, et ε >= 0")
    carre_moyen = sum(v * v for v in x) / d
    if carre_moyen + eps == 0:
        raise ValueError("vecteur nul et ε = 0 : 0/0")
    rms = math.sqrt(carre_moyen + eps)
    return [g * v / rms for v, g in zip(x, gamma)]


def batch_norm_entrainement(lot: list[list[float]], eps: float = 1e-5) -> list[list[float]]:
    """Comparaison : BatchNorm (mode entraînement) normalise chaque coordonnée À TRAVERS les tokens du lot."""
    colonnes = [list(c) for c in zip(*lot)]
    stats = [(moyenne(c), variance(c)) for c in colonnes]
    return [[(v - m) / math.sqrt(s + eps) for v, (m, s) in zip(token, stats)] for token in lot]


def ecart_max(u: list[float], v: list[float]) -> float:
    return max(abs(a - b) for a, b in zip(u, v))


def arrondir(v: list[float], n: int = 4) -> list[float]:
    return [round(a, n) + 0.0 for a in v]  # + 0.0 transforme un éventuel -0.0 en 0.0 à l'affichage


def main() -> None:
    x = [2.0, 0.0, 4.0, 2.0]

    print("1. LayerNorm sur x = [2, 0, 4, 2]")
    x_hat = layer_norm(x)
    print(f"  μ = {moyenne(x)} ; σ² = {variance(x)} ; x̂ = {arrondir(x_hat, 5)}")
    print(f"  moyenne de x̂ = {moyenne(x_hat) + 0.0} ; variance de x̂ = {variance(x_hat):.6f} = 2 / (2 + 1e-5)")
    assert moyenne(x) == 2.0 and variance(x) == 2.0 and arrondir(x_hat, 5) == [0.0, -1.41421, 1.41421, 0.0]
    assert abs(moyenne(x_hat)) < 1e-15 and abs(variance(x_hat) - 2 / (2 + 1e-5)) < 1e-12
    avec_d_moins_1 = [(v - 2.0) / math.sqrt(statistics.variance(x) + 1e-5) for v in x]
    print(f"  avec le diviseur d − 1 (statistics.variance = {statistics.variance(x):.4f}) : {arrondir(avec_d_moins_1)}")
    assert statistics.pvariance(x) == 2.0 and abs(statistics.variance(x) - 8 / 3) < 1e-12
    assert arrondir(avec_d_moins_1) == [0.0, -1.2247, 1.2247, 0.0]

    print("2. γ et β rendent l'échelle au modèle")
    y = layer_norm(x, gamma=[2.0] * 4, beta=[1.0] * 4)
    print(f"  γ = 2, β = 1 : y = {arrondir(y)}")
    assert all(abs(a - (2 * b + 1)) < 1e-12 for a, b in zip(y, x_hat))

    print("3. Invariances de LayerNorm")
    transforme = [3 * v + 5 for v in x]
    print(f"  LN(3x + 5) − LN(x) : écart max = {ecart_max(layer_norm(transforme), x_hat):.1e} (ε seul)")
    assert ecart_max(layer_norm(transforme), x_hat) < 1e-5
    assert ecart_max(layer_norm(transforme, eps=0.0), layer_norm(x, eps=0.0)) < 1e-15
    assert ecart_max(layer_norm([-v for v in x], eps=0.0), [-v for v in layer_norm(x, eps=0.0)]) < 1e-15
    norme2 = sum(v * v for v in x_hat)
    print(f"  ‖x̂‖² = {norme2:.6f} ≈ d = 4")
    assert abs(norme2 - 4 * 2 / (2 + 1e-5)) < 1e-12

    print("4. RMSNorm : invariant à l'échelle, pas au décalage")
    r = rms_norm(x)
    r_decale = rms_norm([v + 1 for v in x])
    print(f"  RMSNorm(x)     = {arrondir(r)}  (division par √6)")
    print(f"  RMSNorm(x + 1) = {arrondir(r_decale)}")
    assert arrondir(r) == [0.8165, 0.0, 1.633, 0.8165] and arrondir(r_decale) == [0.9045, 0.3015, 1.5076, 0.9045]
    assert ecart_max(rms_norm([3 * v for v in x], eps=0.0), rms_norm(x, eps=0.0)) < 1e-15
    assert ecart_max(rms_norm([v - 2.0 for v in x]), x_hat) < 1e-15  # RMSNorm du vecteur centré = LayerNorm

    print("5. Token constant [3, 3, 3, 3]")
    constant = [3.0] * 4
    print(f"  avec ε : x̂ = {layer_norm(constant)} ; avec β = 0.5 : y = {layer_norm(constant, beta=[0.5] * 4)}")
    assert layer_norm(constant) == [0.0] * 4 and layer_norm(constant, beta=[0.5] * 4) == [0.5] * 4
    try:
        layer_norm(constant, eps=0.0)
    except ValueError as e:
        print(f"  sans ε : ValueError — {e}")
    else:
        raise AssertionError("0/0 aurait dû être refusé")
    assert not (math.nan > 0.9) and not (math.nan <= 0.9)  # un score NaN ne franchit aucun seuil

    print("6. Sans normalisation, l'échelle explose couche après couche")
    v = x[:]
    for _ in range(10):
        v = [3 * a for a in v]  # une « couche » qui multiplie tout par 3
    print(f"  après 10 couches ×3 : norme × {math.sqrt(sum(a * a for a in v)) / math.sqrt(sum(a * a for a in x)):.0f}"
          f", produit scalaire × {3 ** 20:_} ; après LayerNorm : ‖x̂‖² = {sum(a * a for a in layer_norm(v)):.4f}")
    assert 3 ** 10 == 59_049 and abs(sum(a * a for a in layer_norm(v)) - 4) < 1e-4

    print("7. BatchNorm dépend des voisins du lot, LayerNorm non")
    bn1 = batch_norm_entrainement([x, [0.0] * 4])[0]
    bn2 = batch_norm_entrainement([x, [10.0] * 4])[0]
    print(f"  BN(x) avec un voisin nul : {arrondir(bn1)} ; avec un voisin à 10 : {arrondir(bn2)}")
    assert ecart_max(bn1, bn2) > 0.5 and layer_norm(x) == x_hat

    print("8. Nombres des cas d'usage")
    prix = [1400.0, 1450.0, 1500.0]
    variantes = [[2 * p for p in prix], [p + 200 for p in prix], [p / 3.6725 for p in prix]]
    assert all(ecart_max(layer_norm(w, eps=0.0), layer_norm(prix, eps=0.0)) < 1e-12 for w in variantes)
    presque = [1.0, 1.001, 0.999, 1.0]
    e5, e6 = layer_norm(presque, eps=1e-5)[1], layer_norm(presque, eps=1e-6)[1]
    print(f"  token presque constant : x̂_2 = {e5:.4f} avec ε = 1e-5, {e6:.4f} avec ε = 1e-6")
    assert round(e5, 4) == 0.3086 and round(e6, 4) == 0.8165
    assert ecart_max(layer_norm(x, eps=1e-5), layer_norm(x, eps=1e-6)) < 1e-5

    print("9. Entrées invalides refusées")
    for appel in (lambda: layer_norm([]), lambda: layer_norm(x, gamma=[1.0, 1.0])):
        try:
            appel()
        except ValueError as e:
            print(f"  ValueError : {e}")
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. LayerNorm sur x = [2, 0, 4, 2]
  μ = 2.0 ; σ² = 2.0 ; x̂ = [0.0, -1.41421, 1.41421, 0.0]
  moyenne de x̂ = 0.0 ; variance de x̂ = 0.999995 = 2 / (2 + 1e-5)
  avec le diviseur d − 1 (statistics.variance = 2.6667) : [0.0, -1.2247, 1.2247, 0.0]
2. γ et β rendent l'échelle au modèle
  γ = 2, β = 1 : y = [1.0, -1.8284, 3.8284, 1.0]
…
  LN(3x + 5) − LN(x) : écart max = 3.1e-06 (ε seul)
  ‖x̂‖² = 3.999980 ≈ d = 4
…
  RMSNorm(x)     = [0.8165, 0.0, 1.633, 0.8165]  (division par √6)
  RMSNorm(x + 1) = [0.9045, 0.3015, 1.5076, 0.9045]
…
  avec ε : x̂ = [0.0, 0.0, 0.0, 0.0] ; avec β = 0.5 : y = [0.5, 0.5, 0.5, 0.5]
…
  BN(x) avec un voisin nul : [1.0, 0.0, 1.0, 1.0] ; avec un voisin à 10 : [-1.0, -1.0, -1.0, -1.0]
…
  token presque constant : x̂_2 = 0.3086 avec ε = 1e-5, 0.8165 avec ε = 1e-6
…
OK — toutes les vérifications sont passées.
```

### La version PyTorch (extrait)

L'ancien bloc était le seul code de ce fichier ; il est juste, mais dépend de PyTorch. Le voici en extrait, complété d'une RMSNorm :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`LayerNorm.__init__(d_model, eps)`** — Le constructeur prépare l'établi du tailleur avant le premier essayage : il reçoit la largeur `d_model` des tokens et ε, 10⁻⁵ par défaut, puis crée deux paramètres apprenables, γ rempli de 1 et β rempli de 0, de sorte qu'au départ de l'entraînement la couche rende exactement x̂, et range ε pour plus tard. Il ne renvoie rien ; ce sont ces deux vecteurs de `d_model` nombres que l'optimiseur ajustera ensuite, comme les arguments `gamma` et `beta` de `layer_norm` dans le programme en Python pur.

**`LayerNorm.forward(x)`** — Cette méthode fait le travail du tailleur sur tout un lot de tokens à la fois : elle reçoit un tenseur x dont la dernière dimension porte les coordonnées de chaque token, calcule la moyenne et la variance le long de cette dimension, avec `unbiased=False` pour diviser par d et non par d − 1, normalise par √(σ² + ε), puis applique γ et β. Elle renvoie un tenseur de même forme que x, et c'est la même formule que `layer_norm` du programme précédent, appliquée d'un coup à chaque token au lieu d'une boucle.

**`RMSNorm.__init__(d_model, eps)`** — Le constructeur de la variante pressée n'installe qu'un seul jeu d'outils : il reçoit la largeur `d_model` et ε, qui vaut ici 10⁻⁶ par défaut et non 10⁻⁵, crée un paramètre apprenable γ rempli de 1 et range ε, sans aucun β, puisque RMSNorm ne décale jamais la sortie. Il ne renvoie rien ; la couche ne possède donc que `d_model` paramètres, moitié moins qu'une LayerNorm de même largeur, une petite économie qui s'ajoute à celle du calcul de la moyenne évoquée au point 4.

**`RMSNorm.forward(x)`** — Cette méthode ajuste l'échelle de chaque token sans le recentrer : elle reçoit un tenseur x, élève chaque coordonnée au carré, en fait la moyenne le long de la dernière dimension, ajoute ε et prend la racine, puis divise x par ce nombre et multiplie le résultat par γ. Elle renvoie un tenseur de même forme que x ; c'est la formule de `rms_norm` du programme en Python pur, sans soustraction de la moyenne, si bien que multiplier un token par 3 ne change pas sa sortie alors que lui ajouter 1 la change.

```python
# [extrait] — version PyTorch, non exécutée par le harnais (PyTorch n'est pas dans la bibliothèque standard)
import torch
import torch.nn as nn


class LayerNorm(nn.Module):
    def __init__(self, d_model, eps=1e-5):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)                 # moyenne sur les coordonnées du token
        var = x.var(dim=-1, keepdim=True, unbiased=False)   # diviseur d ; le défaut (unbiased=True) diviserait par d − 1
        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta


class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.eps = eps

    def forward(self, x):
        return self.gamma * x / torch.sqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
```

`mean = x.mean(dim=-1)` moyenne la dernière dimension, celle des coordonnées, pas le lot ni la séquence ; `keepdim=True` garde une dimension de taille 1 pour que `x - mean` s'aligne sur chaque case. `var(..., unbiased=False)` divise par d : avec le défaut de PyTorch, `unbiased=True`, la variance de l'exemple vaudrait 8/3 au lieu de 2, et γ et β apprendraient à compenser un écart qui n'est pas celui de la formule. `gamma` part à 1 et `beta` à 0, donc au premier pas la sortie vaut x̂ ; le réseau a ensuite le droit de réétaler. `dim=-1` est le choix qui distingue LayerNorm de BatchNorm, qui moyennerait à travers les phrases du lot (point 7).

## Squelette algorithmique

La normalisation de couche recentre et réduit chaque vecteur sur ses propres coordonnées, puis lui rend une échelle et un décalage appris. RMSNorm retire le recentrage, et la normalisation par lot normalise au contraire chaque coordonnée à travers le lot.

```text
ALGORITHME LayerNorm
ENTRÉES : vecteur x (dimension d), γ et β (dimension d, par défaut 1 et 0), ε
SORTIE  : y (dimension d)

  μ ← (Σᵢ xᵢ) / d
  σ² ← (Σᵢ (xᵢ − μ)²) / d
  POUR i DE 1 À d FAIRE
      x̂ᵢ ← (xᵢ − μ) / √(σ² + ε)
      yᵢ ← γᵢ × x̂ᵢ + βᵢ
  FIN POUR
  RETOURNER y

VARIANTE RMSNorm   : rms ← √((Σᵢ xᵢ²) / d + ε) ; yᵢ ← γᵢ × xᵢ / rms          (pas de μ, pas de β)
VARIANTE BatchNorm : pour chaque coordonnée i, μᵢ et σᵢ² sont calculés sur les vecteurs du lot
```

**Complexité.** LayerNorm coûte O(d) par vecteur, en deux passes (moyenne, puis variance) : c'est négligeable devant l'attention et les couches denses. Elle ne dépend d'aucun autre vecteur, contrairement à BatchNorm qui coûte O(B × d) pour un lot de B vecteurs et change de comportement entre l'entraînement et l'inférence. ε évite la division par zéro quand toutes les coordonnées sont égales.

**Du squelette au code.** `moyenne` et `variance` calculent μ et σ², `layer_norm` l'algorithme complet, `rms_norm` la première variante et `batch_norm_entrainement` la seconde. Les classes PyTorch `LayerNorm` et `RMSNorm`, plus bas, font les mêmes calculs sur des tenseurs.

## Cas d'usage réels aux Émirats

Les montants, seuils et volumes ci-dessous sont illustratifs ; les nombres issus d'une formule sont vérifiés par le programme (bloc 8).

### Immobilier — un modèle maison qui ne voit plus le niveau des prix

Une agence et un promoteur à Dubaï et Abu Dhabi entraînent un petit modèle Transformer qui lit, pour chaque tour, la série des prix médians mensuels en AED/sqft et prédit la tendance du trimestre suivant. Chaque série passe par une LayerNorm avant l'attention. Or LayerNorm efface le niveau et l'échelle (point 3) : la série [1 400 ; 1 450 ; 1 500], la même série doublée, la même décalée de 200 AED/sqft et la même convertie en USD au taux fixe de 3,6725 donnent exactement le même vecteur normalisé, ce que le programme vérifie. Pour la tendance, c'est voulu : le modèle apprend la forme de la courbe, quelle que soit la tour. Mais si l'équipe veut aussi estimer un prix, ou distinguer une tour à 1 400 AED/sqft d'une tour à 2 800, le niveau doit entrer autrement, par exemple comme une caractéristique séparée (le logarithme du prix médian) qui n'est pas normalisée avec la série. Sans cette précaution, le modèle produit des tendances plausibles mais il est incapable de dire si un bien est cher, et l'équipe peut croire à tort qu'il « ne comprend pas les prix ». L'indicateur suivi est l'erreur de prédiction de la tendance, et séparément celle du niveau de prix, sur les transactions DLD du trimestre suivant.

### Crypto — une fenêtre sans activité qui éteint une alerte

Une plateforme d'actifs virtuels agréée par la VARA fait tourner un petit modèle de détection d'anomalies sur des fenêtres de cinq minutes de chaque pool : volumes, nombre d'ordres, écart de prix. Une nuit, un pool peu liquide n'enregistre aucune transaction pendant plusieurs fenêtres : toutes ses caractéristiques valent 0, le token est constant et sa variance est nulle. Dans une implémentation réécrite sans ε, la normalisation calcule 0/0 et produit un NaN, qui se propage jusqu'au score d'anomalie (point 5). La règle d'alerte « score > 0,9 » est alors fausse — mais « score ≤ 0,9 » l'est aussi : aucune alerte ne part, et aucun message d'erreur ne s'affiche. Avec ε, le même token donne x̂ = 0 et une sortie égale à β, un résultat défini que le modèle a appris à traiter. L'équipe garde donc l'ε de la configuration d'origine, ajoute un contrôle `math.isnan` sur chaque score avant la règle d'alerte, et traite un NaN comme un incident technique qui déclenche lui-même une alerte. Sans ce contrôle, un pool pourrait être manipulé pendant une période calme sans qu'aucune alerte ne parvienne à l'astreinte. L'indicateur suivi est le nombre de scores NaN détectés par jour, avec un objectif de zéro.

### RH — BatchNorm et la composition du lot

Un cabinet RH multi-émirats a entraîné un petit classifieur qui trie les messages des candidats (visa, contrat, salaire, autre). La première version, reprise d'un tutoriel de vision, utilisait BatchNorm ; en production, un message reçoit parfois deux catégories différentes selon les messages traités dans le même lot. Le point 7 explique pourquoi : en mode entraînement, BatchNorm normalise chaque coordonnée à travers le lot, et la sortie d'un même token passe de [1 ; 0 ; 1 ; 1] à [−1 ; −1 ; −1 ; −1] selon son voisin. L'erreur venait d'un service resté en mode entraînement ; en mode inférence, BatchNorm aurait utilisé ses statistiques courantes, figées, mais calculées sur les données d'entraînement, alors que la part des messages en arabe avait augmenté depuis. L'équipe remplace BatchNorm par LayerNorm, qui ne dépend que du message lui-même, et ajoute un test : le même message, envoyé seul puis au milieu de 31 autres, doit recevoir exactement la même catégorie. Sans ce test, un candidat dont la question de visa est classée « autre » attend une réponse qui ne vient pas. L'indicateur suivi est le taux de messages dont la catégorie change entre deux passages, avec un objectif de zéro.

### Assurance — un portage qui divise par d − 1

Un assureur auto et santé réimplémente en Python, pour un service interne d'analyse de sinistres, la couche de normalisation d'un modèle entraîné avec PyTorch. Le développeur utilise `statistics.variance`, qui divise par d − 1, au lieu de `statistics.pvariance`, qui divise par d. Sur l'exemple [2, 0, 4, 2], la variance passe de 2 à 2,6667 et x̂ de [0 ; −1,4142 ; 1,4142 ; 0] à [0 ; −1,2247 ; 1,2247 ; 0] : chaque couche décale un peu les activations, et après des dizaines de couches les classements de fraude ne sont plus ceux du modèle validé. Le défaut ne fait planter aucun test qui se contente de vérifier la forme des sorties. L'équipe ajoute donc un test d'oracle : sur des entrées fixes, la couche réimplémentée doit redonner les sorties de la référence à 10⁻⁶ près, ce qui détecte l'écart dès la première couche. Sans ce test, des sinistres frauduleux peuvent passer sous le seuil de revue, alors que l'assureur, supervisé par la CBUAE, doit pouvoir expliquer ses décisions. L'indicateur suivi est l'écart maximal entre la réimplémentation et la référence, contrôlé à chaque mise en production.

### Secteur public — un ε qui ne correspond pas à la configuration

Une entité de services publics en ligne accessible par UAE Pass déploie un modèle bilingue dans un nouveau moteur d'inférence. Le fichier de configuration du modèle indique ε = 10⁻⁶ pour ses normalisations, mais le moteur applique par défaut ε = 10⁻⁵. Pour un token ordinaire, la différence est invisible : sur [2, 0, 4, 2], la sortie change de moins de 10⁻⁵. Pour un token presque constant, comme [1 ; 1,001 ; 0,999 ; 1], de variance 5 × 10⁻⁷, ε domine le dénominateur et la même coordonnée vaut 0,3086 avec ε = 10⁻⁵ contre 0,8165 avec ε = 10⁻⁶ (point 5 et bloc 8). L'écart n'apparaît donc que sur certains tokens, et les réponses divergent de temps en temps, sans motif évident. L'équipe lit les ε dans la configuration au lieu de garder les valeurs par défaut, et ajoute au jeu de tests de déploiement des vecteurs presque constants, ceux qui révèlent ce type d'écart. Sans cela, l'usager peut recevoir une réponse différente de celle validée en recette pour la même question, ce qui fragilise la confiance dans un service public. L'indicateur suivi est le taux de réponses identiques entre l'environnement de recette et la production sur un jeu de questions fixes.

## Pièges et limites

- **Diviser par d − 1.** `statistics.variance` et `torch.var` par défaut divisent par d − 1 ; la formule divise par d (`statistics.pvariance`, `unbiased=False`).
- **Supprimer ε.** Un token constant donne alors 0/0, donc NaN dans NumPy ou PyTorch, et un NaN ne franchit aucun seuil.
- **Oublier ce que LayerNorm efface.** Niveau et échelle d'entrée disparaissent ; s'ils comptent, ils doivent entrer par un autre chemin.
- **Croire RMSNorm invariante au décalage.** Elle ne l'est qu'à l'échelle (point 4).
- **Laisser un modèle à BatchNorm en mode entraînement.** Sa sortie dépend alors des autres éléments du lot ; LayerNorm n'a pas ce problème.

### Exercice feuille blanche

1. Sans regarder le code, écrire `layer_norm` et `rms_norm`, puis retrouver [0, −1,41421, 1,41421, 0] et [0,8165, 0, 1,633, 0,8165] pour x = [2, 0, 4, 2].
2. Prédire, puis vérifier : que donne LayerNorm sur [−2, 0, −4, −2] ? (Réponse : [0, 1,41421, −1,41421, 0], puisque LayerNorm(−x) = −LayerNorm(x).)
3. Trouver le bug : `ecart = math.sqrt(var) + eps` à la place de `math.sqrt(var + eps)`. Que vaut la sortie pour le token constant [3, 3, 3, 3], et en quoi cette version diffère-t-elle de la formule pour [2, 0, 4, 2] ? (Réponse : pour le token constant, 0 / 10⁻⁵ = 0, donc le résultat reste défini ; mais pour [2, 0, 4, 2], le dénominateur vaut √2 + 10⁻⁵ au lieu de √(2 + 10⁻⁵) : la différence est minime ici, mais ce n'est plus la formule, et les sorties ne coïncideront pas exactement avec celles du modèle d'origine.)

## Pour aller plus loin

Le Transformer d'origine place la normalisation après chaque sous-couche (post-norm) ; la plupart des modèles récents la placent avant (pre-norm), ce qui stabilise l'entraînement de réseaux très profonds. Certaines architectures normalisent aussi les requêtes et les clés avant l'attention, pour limiter la croissance des scores au cours de l'entraînement (étape 32).

> Suite : [Mélange d'experts (MoE)](<36b-Melange-d-Experts-MoE.md>) — étape 36 bis.
