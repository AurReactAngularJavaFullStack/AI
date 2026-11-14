# Étape 52 — Perplexité — Métrique Fondamentale d'Évaluation des LLM

> Étape 52 du parcours · Prérequis : [Spécificité, VPN et AUC](<51-Specificite-NPV-AUC.md>) · Suite : [Évaluation : formules, théorèmes et algorithmes](<53-Evaluation-Formules-Theoremes-Algorithmes.md>)

**Dossier :** 10-Evaluation  
**Métiers concernés :** AI Engineers, AI Agent Ops

## Définition

La perplexité mesure à quel point un modèle de langage est « surpris » par un texte de référence, celui qu'un humain a vraiment écrit. À chaque position, on regarde la probabilité que le modèle donnait au token qui est réellement venu ensuite, sachant tous les tokens précédents. La perplexité est l'inverse de la moyenne géométrique de ces probabilités, ou, ce qui revient au même, l'exponentielle de l'entropie croisée moyenne par token. Une perplexité de k se lit « à chaque token, le modèle hésitait comme entre k candidats également plausibles » : elle vaut au minimum 1 (prédiction parfaite), vaut exactement |V| pour un modèle qui tire au hasard parmi les |V| tokens du vocabulaire, et peut dépasser |V| sans limite quand le modèle est sûr de lui et se trompe.

## Rôle dans un agent

La perplexité ne sert pas à chaque tour de boucle : elle juge le **modèle** qui sert de cerveau à l'agent, et les **textes** qu'il reçoit. Au moment **observer**, elle compare un modèle avant et après une adaptation au métier (fine-tuning, étape 73) sur un jeu de textes du domaine tenu à part. Au moment **percevoir**, elle sert de détecteur de texte inhabituel : un document dont la perplexité, sous un modèle de référence, est très au-dessus de la normale (OCR raté, langue inattendue, texte hors domaine) part en revue au lieu d'être injecté tel quel dans le RAG. Elle sert aussi à surveiller une dérive : si la perplexité moyenne des messages entrants monte d'une semaine à l'autre, le vocabulaire des clients a changé. Elle exige les log-probabilités des tokens, que toutes les API n'exposent pas, et l'étape 62 en donne la version métier.

## Équation complète

Forme produit :

$$
\text{PPL}(W) = \sqrt[N]{\prod_{i=1}^{N} \frac{1}{P(w_i \mid w_{1:i-1})}}
$$

Forme logarithmique (celle qu'on calcule) :

$$
\text{PPL}(W) = \exp\left( -\frac{1}{N} \sum_{i=1}^{N} \ln P(w_i \mid w_{1:i-1}) \right)
$$

Relation avec l'entropie croisée moyenne par token :

$$
\text{PPL} = \exp\bigl( H(P_{\text{vrai}}, Q_{\text{modèle}}) \bigr)
$$

Comparaison avant / après une adaptation, positive quand le modèle s'améliore :

$$
\Delta\text{PPL} = \text{PPL}_{\text{avant}} - \text{PPL}_{\text{après}}
$$

Ce qui est borné par la taille du vocabulaire, c'est l'entropie propre d'une distribution Q, pas la perplexité sur un texte :

$$
1 \le \text{PPL} \qquad \text{et} \qquad \exp\bigl(H(Q)\bigr) \le |V|
$$

## Décryptage des symboles

$$
W = (w_1, \dots, w_N)
$$

**Sens :** le texte de référence, découpé en N tokens par le tokenizer du modèle · **Type / plage :** suite de N ≥ 1 tokens · **Variable Python :** `test` (liste de mots dans le programme).

$$
P(w_i \mid w_{1:i-1})
$$

**Sens :** probabilité que le modèle donnait au token réel wᵢ, sachant les i − 1 tokens précédents · **Type / plage :** réel dans [0, 1] · **Variable Python :** chaque élément de `probas`.

$$
N
$$

**Sens :** nombre de prédictions notées (le premier token, sans contexte, ne l'est pas toujours) · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(probas)`.

$$
H(P_{\text{vrai}}, Q_{\text{modèle}})
$$

**Sens :** entropie croisée moyenne par token, entre le texte réel (un token certain à chaque position) et les probabilités du modèle · **Type / plage :** réel ≥ 0, en nats avec ln · **Variable Python :** `h_nats`.

$$
|V|
$$

**Sens :** taille du vocabulaire du tokenizer · **Type / plage :** entier, de quelques dizaines de milliers à plus de cent mille pour un LLM, 13 dans le programme · **Variable Python :** `len(vocab)`.

$$
H(Q)
$$

**Sens :** entropie d'une distribution Q du modèle sur le vocabulaire, son incertitude propre · **Type / plage :** réel entre 0 et ln |V| · **Variable Python :** `entropie(Q)`.

$$
\Delta\text{PPL}
$$

**Sens :** gain de perplexité, avant moins après · **Type / plage :** réel ; positif si le modèle est moins surpris après · **Variable Python :** `ppl_av - ppl_ap`.

## Démonstration

### 1. La forme produit et la forme logarithmique sont la même quantité

On prend le logarithme de la forme produit. Le logarithme d'une racine N-ième est le logarithme divisé par N, et le logarithme d'un produit est la somme des logarithmes :

$$
\ln \text{PPL} = \frac{1}{N} \ln \prod_{i=1}^{N} \frac{1}{p_i} = \frac{1}{N} \sum_{i=1}^{N} \ln\frac{1}{p_i} = -\frac{1}{N} \sum_{i=1}^{N} \ln p_i
$$

où pᵢ abrège P(wᵢ | w₁…wᵢ₋₁). On applique l'exponentielle des deux côtés, parce que exp(ln x) = x, et on obtient la forme logarithmique. Les deux formes sont égales en mathématiques ; seule la forme logarithmique survit aux flottants (point 6).

### 2. La perplexité est l'exponentielle d'une entropie croisée

À la position i, la « vraie » distribution est certaine : elle met la probabilité 1 sur le token réel wᵢ et 0 ailleurs. L'entropie croisée de l'étape 50, H(P, Q) = −∑ P ln Q, ne garde alors qu'un terme, −ln Q(wᵢ). La moyenne sur les N positions est exactement l'exposant de la forme logarithmique :

$$
H(P_{\text{vrai}}, Q_{\text{modèle}}) = -\frac{1}{N} \sum_{i=1}^{N} \ln Q(w_i \mid w_{1:i-1})
\quad\Longrightarrow\quad
\text{PPL} = e^{H}
$$

C'est aussi la perte d'entraînement d'un LLM : la perplexité est l'exponentielle de la perte moyenne. La base du logarithme ne change pas le résultat : en bits, H₂ = H / ln 2, et 2 à la puissance H₂ vaut e à la puissance H. Sur l'exemple, H = 0,99858 nat = 1,44064 bit, et les deux donnent 2,7144.

### 3. La perplexité est toujours au moins 1

Chaque probabilité vérifie 0 < pᵢ ≤ 1, donc ln pᵢ ≤ 0, parce que le logarithme est croissant et vaut 0 en 1. La moyenne des −ln pᵢ est donc positive, et l'exponentielle d'un nombre positif est au moins e⁰ = 1 :

$$
-\frac{1}{N}\sum_{i=1}^{N} \ln p_i \ge 0 \quad\Longrightarrow\quad \text{PPL} \ge 1
$$

L'égalité a lieu si et seulement si tous les pᵢ valent 1 : le modèle prédisait chaque token réel avec certitude. Si un pᵢ vaut 0, son logarithme vaut −∞ et la perplexité est infinie : le modèle avait exclu le token qui est vraiment là.

### 4. Un modèle uniforme a une perplexité égale à |V|

Si le modèle donne la même probabilité 1/|V| à chaque token, chaque pᵢ vaut 1/|V| et

$$
\text{PPL} = \exp\left(-\frac{1}{N}\sum_{i=1}^{N} \ln\frac{1}{|V|}\right) = \exp(\ln |V|) = |V|
$$

Plus généralement, un modèle qui donne 1/k au token réel à chaque position a une perplexité de k : c'est la lecture « facteur de branchement effectif ». Avec un vocabulaire de 50 000 tokens, tirer au hasard donne 50 000, pas « plus de 200 » comme le disait l'ancien tableau.

### 5. « PPL ≤ |V| » est faux ; ce qui est vrai, c'est exp(H(Q)) ≤ |V|

**Contre-exemple.** Vocabulaire de 4 tokens. Le modèle met 0,97 sur le token 0 et 0,01 sur chacun des trois autres, mais le texte réel est toujours le token 1. Chaque pᵢ vaut 0,01 et la perplexité vaut 1/0,01 = 100, soit 25 fois |V|. Un modèle sûr de lui et faux fait **pire** que le hasard, et il n'y a pas de plafond : quand pᵢ tend vers 0, la perplexité tend vers +∞.

**Ce qui est borné.** L'entropie propre d'une distribution Q sur |V| tokens vérifie H(Q) ≤ ln |V|. On la compare à la distribution uniforme U, qui vaut 1/|V| partout, avec la KL de l'étape 50 :

$$
D_{KL}(Q \parallel U) = \sum_x Q(x)\ln\frac{Q(x)}{1/|V|} = \sum_x Q(x)\ln Q(x) + \ln|V| \sum_x Q(x) = -H(Q) + \ln |V|
$$

L'inégalité de Gibbs (étape 50, point 7) dit que cette KL est positive, donc H(Q) ≤ ln |V|, avec égalité si et seulement si Q est uniforme. En prenant l'exponentielle, exp(H(Q)) ≤ |V|. Sur le contre-exemple, H(Q) = 0,1677 et exp(H(Q)) = 1,18 : le modèle se croit presque certain (1,18 candidat), alors que sa perplexité sur le texte réel vaut 100.

**Le lien entre les deux.** Si le texte suit une vraie loi P, l'entropie croisée attendue vaut H(P) + D_KL(P‖Q) (étape 50, point 6). La perplexité attendue est donc exp(H(P)) multipliée par exp(D_KL(P‖Q)) : la première partie est l'incertitude irréductible de la langue, que personne ne peut descendre ; la seconde est l'erreur du modèle, qui n'a pas de borne.

### 6. Le produit sous-déborde, la somme des logarithmes non

L'ancienne version disait que « vingt tokens à 0,1 donnent 10²⁰, qui déborde un flottant ». C'est faux : le plus grand flottant double vaut environ 1,8 × 10³⁰⁸, et 10²⁰ en est très loin. Le vrai danger est à l'autre bout : le produit des probabilités devient trop petit. Le plus petit flottant positif représentable vaut environ 4,9 × 10⁻³²⁴, donc 0,1ⁿ s'arrondit à 0 dès n = 324 tokens. Un document de quelques milliers de tokens donne un produit égal à 0, et la racine N-ième de 0 à une puissance négative lève `ZeroDivisionError`. La forme logarithmique additionne N nombres de taille modeste (ici −2,3026 chacun) et ne déborde jamais.

### 7. ΔPPL positif veut dire que le modèle s'améliore

Avec ΔPPL = PPL avant − PPL après, une perplexité qui baisse donne un ΔPPL **positif** : le modèle est moins surpris par les textes du métier. L'ancienne version disait l'inverse. Comme la perplexité est une exponentielle, on compare aussi souvent les entropies croisées : ln PPL avant − ln PPL après est le gain en nats par token.

### 8. La perplexité dépend du découpage en tokens

Découpons « annulé » en deux sous-mots, « annul » puis « é », avec les probabilités 0,25 et 0,8. Leur produit, 0,2, est la probabilité que le modèle par mots donnait à « annulé » : les deux modèles donnent la même probabilité à la phrase entière. Pourtant, N passe de 3 à 4, et

$$
\text{PPL}_{\text{mot}} = 20^{1/3} = 2{,}7144
\qquad
\text{PPL}_{\text{sous-mot}} = 20^{1/4} = 2{,}1147
$$

Deux modèles qui n'ont pas le même tokenizer ne se comparent donc pas par leur perplexité par token. On compare la log-vraisemblance totale du même texte, ou une perplexité ramenée au mot ou au caractère.

### 9. Exemple fait à la main (le code reprend ces nombres)

**La phrase « le vol est annulé ».** Le modèle a donné 0,5 à « vol » après « le », 0,5 à « est », 0,2 à « annulé ». Forme produit : 1/0,5 × 1/0,5 × 1/0,2 = 20, et la racine cubique de 20 vaut 2,7144. Forme logarithmique :

$$
-\frac{1}{3}\bigl(\ln 0{,}5 + \ln 0{,}5 + \ln 0{,}2\bigr) = -\frac{1}{3}(-0{,}69315 - 0{,}69315 - 1{,}60944) = 0{,}99858
$$

et e⁰,⁹⁹⁸⁵⁸ = 2,7144.

**Un modèle bigramme avant et après adaptation.** Le vocabulaire a 13 mots. Le modèle « avant » est entraîné sur quatre phrases générales (vols, loyer) ; le modèle « après » reçoit en plus quatre phrases de sinistres. Chaque probabilité est lissée par Laplace : P(b | a) = (c(a, b) + 1) / (c(a) + 13), où c(a, b) compte les passages de a à b et c(a) les passages qui partent de a. Sur la phrase de test « le sinistre est déclaré » :

- avant : 5/17, 1/18, 1/13 et 1/16, soit 0,2941, 0,0556, 0,0769 et 0,0625 ; la perplexité vaut la racine quatrième de 17 × 18 × 13 × 16 / 5 = 12 729,6, soit 10,622 ;
- après : 9/21, 5/23, 4/16 et 2/19, soit 0,4286, 0,2174, 0,25 et 0,1053 ; la perplexité vaut 4,494 ;
- ΔPPL = 10,622 − 4,494 = 6,128 > 0 : l'adaptation a servi. Les deux restent sous |V| = 13, parce qu'ils font mieux que le hasard sur ce texte.

## Effets et comportement

| Perplexité | Ce qu'elle veut dire |
|---|---|
| 1 | prédiction parfaite : le token réel avait toujours la probabilité 1 (théorique) |
| k | à chaque token, l'hésitation équivaut à k candidats également plausibles |
| \|V\| | le modèle ne fait pas mieux qu'un tirage uniforme dans le vocabulaire |
| au-dessus de \|V\| | le modèle fait pire que le hasard : il est sûr de lui et se trompe |
| +∞ | au moins un token réel avait la probabilité 0 |

Les valeurs « bonnes » d'un vrai LLM dépendent du tokenizer, du domaine et du jeu de test : elles ne se comparent qu'à tokenizer et à jeu de test identiques. Une perplexité basse veut dire que le texte ressemble à ce que le modèle attend, pas qu'il est vrai : un modèle peut produire une hallucination très fluide avec une perplexité faible, et un texte qui se répète en boucle a une perplexité très basse.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| pᵢ = P(wᵢ \| w₁…wᵢ₋₁) | éléments de `probas`, ou `Bigramme.proba(prec, mot)` |
| PPL, forme log | `perplexite(probas)` |
| PPL, forme produit | `perplexite_produit(probas)` |
| H en nats et en bits | `h_nats`, `h_bits` |
| H(Q) | `entropie(Q)` |
| \|V\| | `len(vocab)` |
| ΔPPL | `ppl_av - ppl_ap` |

### Déroulé, ligne par ligne

**`perplexite(probas)`**.

- `if not probas: return None` : sans token noté, la moyenne n'existe pas. C'est la convention du parcours pour une métrique sans dénominateur.
- `if not 0.0 <= p <= 1.0` : une « probabilité » de 1,2 est un bug en amont ; on lève `ValueError`.
- `if p == 0.0: return math.inf` : le token réel était impossible pour le modèle, la surprise n'a pas de borne.
- `somme_log += math.log(p)` accumule ∑ ln pᵢ ; pour [0,5 ; 0,5 ; 0,2], elle vaut −2,99573.
- `math.exp(-somme_log / len(probas))` : diviser par N est le 1/N de la formule, le signe moins retourne une somme négative en surprise positive, `exp` sort de l'échelle logarithmique. Résultat : e⁰,⁹⁹⁸⁵⁸ = 2,7144.

**`perplexite_produit(probas)`** calcule `math.prod(probas) ** (-1 / len(probas))`. Sur 3 tokens, elle donne aussi 2,7144. Sur 400 tokens à 0,1, `math.prod` vaut 0.0 et `0.0 ** (-1 / 400)` lève `ZeroDivisionError`.

**`entropie(Q)`** renvoie −∑ q ln q sur les q > 0 : 0,1677 pour (0,97 ; 0,01 ; 0,01 ; 0,01), ln 4 = 1,3863 pour l'uniforme sur 4.

**`Bigramme`**.

- `__init__` parcourt chaque phrase précédée du marqueur `<s>`. Pour chaque couple de mots consécutifs, `comptes[(a, b)]` compte le passage de a à b et `contextes[a]` le nombre de passages qui partent de a. Un mot hors du vocabulaire lève `ValueError`.
- `proba(prec, mot)` applique le lissage de Laplace : `(comptes[(prec, mot)] + 1) / (contextes[prec] + len(self.vocab))`. Pour « sinistre » après « le » dans le modèle « avant », le compte vaut 0 et le contexte 5, d'où 1/18.
- `probas_du_texte(phrase)` renvoie la liste des pᵢ de la phrase, prête pour `perplexite`.

**`main()`**, bloc par bloc.

1. L'exemple à trois tokens : forme produit et forme log égales, puis la même perplexité en nats et en bits.
2. Tout à 1 donne 1 ; l'uniforme sur 4 tokens donne 4, l'uniforme sur 50 000 donne 50 000.
3. Le contre-exemple : perplexité 100 sur un vocabulaire de 4, alors que exp(H(Q)) = 1,18. Trois distributions vérifient H ≤ ln 4, avec égalité pour l'uniforme.
4. `n0` cherche le premier n pour lequel 0,1ⁿ vaut 0.0 : 324. Puis la forme produit plante sur 400 tokens, la forme log donne 10.
5. Les deux bigrammes. La boucle vérifie que chaque loi conditionnelle somme à 1 sur le vocabulaire (sinon ce ne serait pas une probabilité). Puis les perplexités 10,622 et 4,494, et ΔPPL = 6,128 > 0.
6. Le découpage en sous-mots : même probabilité de phrase (0,05), perplexités 2,7144 et 2,1147.
7. Les cas limites : liste vide, probabilité nulle, probabilité 1,2.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`perplexite(probas)`** — Cette fonction est le juge qui mesure à quel point le modèle a été surpris, token après token, par le texte réel : elle reçoit la liste des probabilités que le modèle accordait à chaque token effectivement présent, renvoie `None` si la liste est vide, lève `ValueError` pour une valeur hors de [0 ; 1] et renvoie l'infini dès qu'un token réel avait la probabilité 0. Sinon, elle additionne les logarithmes népériens, divise par le nombre de tokens, change le signe et repasse à l'exponentielle, ce qui donne exp(−(1/N) Σ ln pᵢ) : 2,7144 pour les trois prédictions 0,5, 0,5 et 0,2, c'est-à-dire la racine cubique de 20, et exactement 10 pour 400 tokens à 0,1, là où la forme produit s'effondre.

**`perplexite_produit(probas)`** — Celle-ci est la version naïve du même calcul, celle qu'un élève recopie directement depuis la définition : elle reçoit la liste des probabilités, les multiplie toutes avec `math.prod` et élève ce produit à la puissance −1/N, sans aucune garde. Elle renvoie le même 2,7144 que `perplexite` sur trois tokens et 10 sur vingt tokens à 0,1, mais le produit de 400 probabilités à 0,1 sous-déborde en 0.0 dès 324 facteurs, et la puissance négative de zéro lève alors `ZeroDivisionError` : `main` la garde précisément pour montrer pourquoi on calcule la perplexité par la somme des logarithmes.

**`entropie(Q)`** — Cette fonction mesure l'incertitude que le modèle affiche lui-même, avant de connaître le texte, comme un parieur qui répartit ses mises : elle reçoit une distribution Q sur le vocabulaire, ignore les probabilités nulles et renvoie −Σ q ln q, en nats. Pour le modèle qui mise 0,97 sur un token et 0,01 sur chacun des trois autres, elle vaut 0,1677, d'où exp(H) = 1,1826, bien en dessous de 4 ; pour l'uniforme sur 4 tokens, elle vaut ln 4 = 1,3863. `main` s'en sert pour montrer que l'entropie est bornée par ln |V|, alors que la perplexité mesurée sur un texte réel, ici 100, ne l'est pas.

**`Bigramme.__init__(corpus, vocab)`** — Le constructeur est l'apprenti scribe qui lit tout un recueil de phrases pour retenir quel mot suit quel autre : il reçoit un corpus, une liste de phrases déjà découpées en mots, et un vocabulaire qu'il trie après en avoir retiré les doublons, puis, pour chaque phrase précédée du marqueur `<s>`, il parcourt les couples de mots consécutifs, compte chaque passage de a à b dans `comptes` et chaque départ depuis a dans `contextes`. Il lève `ValueError` si un mot de la phrase n'appartient pas au vocabulaire, et ne renvoie rien ; `main` en construit deux, un modèle « avant » entraîné sur quatre phrases générales et un modèle « après » qui y ajoute quatre phrases du métier de l'assurance.

**`Bigramme.proba(prec, mot)`** — Cette méthode répond à la question que se pose le scribe devant chaque mot : après « prec », quelle chance avait « mot » d'arriver ? Elle reçoit le mot précédent et le mot candidat, lève `ValueError` si le candidat est hors vocabulaire, puis applique le lissage de Laplace, (compte du couple + 1) ÷ (compte du contexte + taille du vocabulaire), qui donne une probabilité non nulle même à un couple jamais vu. Elle renvoie ce nombre : 1/18, soit 0,0556, pour « sinistre » après « le » dans le modèle avant, où le couple n'a jamais été vu et où « le » sert de contexte 5 fois avec un vocabulaire de 13 mots ; `main` vérifie que, pour chaque mot précédent, ces probabilités somment à 1.

**`Bigramme.probas_du_texte(phrase)`** — Celle-ci est le lecteur qui passe une phrase de test au crible du modèle, mot par mot : elle reçoit une liste de mots, la fait précéder du marqueur `<s>`, et renvoie la liste des probabilités que `proba` accorde à chaque mot sachant celui qui le précède. Pour « le sinistre est déclaré », le modèle avant donne 0,2941, 0,0556, 0,0769 et 0,0625, le modèle après 0,4286, 0,2174, 0,25 et 0,1053 ; ces listes, prêtes pour `perplexite`, donnent 10,622 et 4,494, d'où un ΔPPL de 6,128.

**`main()`** — C'est le chef d'orchestre des sept vérifications : il calcule la perplexité 2,7144 des trois prédictions par les deux formes et en nats comme en bits, montre qu'un modèle sûr de lui donne 1 et un modèle uniforme donne la taille du vocabulaire, 4 ou 50 000, puis réfute l'idée que la perplexité serait bornée par |V| avec un texte réel à 100 face à exp(H(Q)) = 1,1826. Il cherche ensuite le seuil de 324 facteurs où 0,1ⁿ devient 0.0 et fait planter la forme produit sur 400 tokens, compare les deux bigrammes, montre que deux découpages de la même phrase donnent 2,7144 et 2,1147 pour une même probabilité 0,05, et termine par la liste vide, la probabilité nulle et la probabilité 1,2 ; « OK » ne s'affiche que si tous les `assert` passent.

```python
"""Étape 52 — perplexité : forme produit et forme log, PPL ≥ 1, borne |V| de l'entropie, ΔPPL, tokenizer."""
import math
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def perplexite(probas: list[float]) -> float | None:
    """PPL = exp(−(1/N) Σ ln p). None si aucun token ; +∞ si le token réel avait la probabilité 0."""
    if not probas:
        return None
    somme_log = 0.0
    for p in probas:
        if not 0.0 <= p <= 1.0:
            raise ValueError("une probabilité est entre 0 et 1")
        if p == 0.0:
            return math.inf          # le modèle avait exclu le token qui est vraiment là
        somme_log += math.log(p)
    return math.exp(-somme_log / len(probas))


def perplexite_produit(probas: list[float]) -> float:
    """(Π p)^(−1/N) : exacte en mathématiques, fragile en flottants (sous-dépassement du produit)."""
    return math.prod(probas) ** (-1 / len(probas))


def entropie(Q: list[float]) -> float:
    """H(Q) = −Σ q ln q, en nats."""
    return -sum(q * math.log(q) for q in Q if q > 0.0)


class Bigramme:
    """Modèle de langue bigramme, lissage de Laplace : P(b | a) = (c(a, b) + 1) / (c(a) + |V|)."""

    def __init__(self, corpus: list[list[str]], vocab: list[str]):
        self.vocab = sorted(set(vocab))
        self.comptes: Counter = Counter()
        self.contextes: Counter = Counter()
        for phrase in corpus:
            jetons = ["<s>"] + phrase
            for a, b in zip(jetons, jetons[1:]):
                if b not in self.vocab:
                    raise ValueError(f"mot hors vocabulaire : {b}")
                self.comptes[(a, b)] += 1
                self.contextes[a] += 1

    def proba(self, prec: str, mot: str) -> float:
        if mot not in self.vocab:
            raise ValueError(f"mot hors vocabulaire : {mot}")
        return (self.comptes[(prec, mot)] + 1) / (self.contextes[prec] + len(self.vocab))

    def probas_du_texte(self, phrase: list[str]) -> list[float]:
        jetons = ["<s>"] + phrase
        return [self.proba(a, b) for a, b in zip(jetons, jetons[1:])]


def main() -> None:
    print("1. « le vol est annulé » : trois prédictions notées")
    probas = [0.5, 0.5, 0.2]
    ppl = perplexite(probas)
    print(f"  produit des inverses = {1 / math.prod(probas):.1f}   PPL = 20^(1/3) = {ppl:.4f}")
    assert abs(ppl - 20 ** (1 / 3)) < 1e-12 and abs(perplexite_produit(probas) - ppl) < 1e-12
    h_nats = -sum(math.log(p) for p in probas) / 3
    h_bits = -sum(math.log2(p) for p in probas) / 3
    print(f"  entropie croisée = {h_nats:.5f} nat = {h_bits:.5f} bit ; e^H = {math.exp(h_nats):.4f} ; 2^H = {2 ** h_bits:.4f}")
    assert abs(math.exp(h_nats) - 2 ** h_bits) < 1e-12        # la base du logarithme ne change pas la PPL

    print("2. PPL ≥ 1, et PPL = |V| pour le modèle uniforme")
    assert perplexite([1.0, 1.0, 1.0]) == 1.0
    print(f"  uniforme sur 4 tokens : {perplexite([0.25] * 7):.4f}   uniforme sur 50 000 : {perplexite([1 / 50000] * 5):.1f}")
    assert abs(perplexite([0.25] * 7) - 4) < 1e-12 and abs(perplexite([1 / 50000] * 5) - 50000) < 1e-6

    print("3. « PPL ≤ |V| » est faux : |V| = 4, le token réel reçoit 0.01")
    Q = [0.97, 0.01, 0.01, 0.01]                            # le modèle parie sur le token 0
    ppl_reelle = perplexite([Q[1]] * 6)                     # le texte réel est toujours le token 1
    h_q = entropie(Q)
    print(f"  PPL sur le texte = {ppl_reelle:.1f} > 4   ;   exp(H(Q)) = {math.exp(h_q):.4f} ≤ 4")
    assert abs(ppl_reelle - 100) < 1e-9 and math.exp(h_q) <= 4
    for D in ([0.25] * 4, [0.7, 0.1, 0.1, 0.1], [1.0, 0.0, 0.0, 0.0]):
        assert entropie(D) <= math.log(4) + 1e-12          # H(Q) ≤ ln |V|, égalité pour l'uniforme
    assert abs(entropie([0.25] * 4) - math.log(4)) < 1e-12

    print("4. Le produit sous-déborde, la somme des logs non")
    n0 = next(n for n in range(1, 2000) if math.prod([0.1] * n) == 0.0)
    print(f"  0.1^20 = {math.prod([0.1] * 20):.1e} (aucun débordement)   0.1^n = 0.0 dès n = {n0}")
    try:
        perplexite_produit([0.1] * 400)
    except ZeroDivisionError:
        print(f"  400 tokens à 0.1 : forme produit → ZeroDivisionError ; forme log → {perplexite([0.1] * 400):.6f}")
    else:
        raise AssertionError("le produit aurait dû valoir 0.0")
    assert abs(perplexite([0.1] * 400) - 10) < 1e-9 and abs(perplexite_produit([0.1] * 20) - 10) < 1e-9

    print("5. ΔPPL = avant − après : positif = le modèle s'améliore")
    vocab = ["le", "vol", "est", "annulé", "retardé", "client", "paie", "loyer", "payé",
             "sinistre", "déclaré", "indemnisé", "expertisé"]
    general = [["le", "vol", "est", "annulé"], ["le", "vol", "est", "retardé"],
               ["le", "client", "paie", "le", "loyer"], ["le", "loyer", "est", "payé"]]
    metier = [["le", "sinistre", "est", "déclaré"], ["le", "sinistre", "est", "indemnisé"],
              ["le", "sinistre", "est", "expertisé"], ["le", "client", "paie", "le", "sinistre"]]
    test = ["le", "sinistre", "est", "déclaré"]
    avant = Bigramme(general, vocab)
    apres = Bigramme(general + metier, vocab)
    for a in avant.vocab:                                   # chaque loi conditionnelle somme à 1
        assert abs(sum(apres.proba(a, b) for b in apres.vocab) - 1) < 1e-12
    p_av, p_ap = avant.probas_du_texte(test), apres.probas_du_texte(test)
    ppl_av, ppl_ap = perplexite(p_av), perplexite(p_ap)
    print(f"  avant : P = {[round(p, 4) for p in p_av]}  PPL = {ppl_av:.3f}")
    print(f"  après : P = {[round(p, 4) for p in p_ap]}  PPL = {ppl_ap:.3f}")
    print(f"  ΔPPL = {ppl_av - ppl_ap:.3f}   |V| = {len(vocab)}")
    assert ppl_av - ppl_ap > 0 and ppl_ap < ppl_av < len(vocab)

    print("6. La même phrase, deux découpages : la PPL change, la vraisemblance non")
    par_mot = [0.5, 0.5, 0.2]
    par_sous_mot = [0.5, 0.5, 0.25, 0.8]                   # « annulé » → « annul » + « é », 0.25 × 0.8 = 0.2
    print(f"  par mot : {perplexite(par_mot):.4f}   par sous-mot : {perplexite(par_sous_mot):.4f}")
    assert abs(math.prod(par_mot) - math.prod(par_sous_mot)) < 1e-12
    assert abs(perplexite(par_sous_mot) - 20 ** 0.25) < 1e-12

    print("7. Cas limites")
    assert perplexite([]) is None and perplexite([0.5, 0.0]) == math.inf
    try:
        perplexite([1.2])
    except ValueError:
        print("  [] → None ; un 0 → inf ; 1.2 → ValueError")
    else:
        raise AssertionError("une probabilité > 1 aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. « le vol est annulé » : trois prédictions notées
  produit des inverses = 20.0   PPL = 20^(1/3) = 2.7144
  entropie croisée = 0.99858 nat = 1.44064 bit ; e^H = 2.7144 ; 2^H = 2.7144
2. PPL ≥ 1, et PPL = |V| pour le modèle uniforme
  uniforme sur 4 tokens : 4.0000   uniforme sur 50 000 : 50000.0
3. « PPL ≤ |V| » est faux : |V| = 4, le token réel reçoit 0.01
  PPL sur le texte = 100.0 > 4   ;   exp(H(Q)) = 1.1826 ≤ 4
4. Le produit sous-déborde, la somme des logs non
  0.1^20 = 1.0e-20 (aucun débordement)   0.1^n = 0.0 dès n = 324
  400 tokens à 0.1 : forme produit → ZeroDivisionError ; forme log → 10.000000
5. ΔPPL = avant − après : positif = le modèle s'améliore
  avant : P = [0.2941, 0.0556, 0.0769, 0.0625]  PPL = 10.622
  après : P = [0.4286, 0.2174, 0.25, 0.1053]  PPL = 4.494
  ΔPPL = 6.128   |V| = 13
6. La même phrase, deux découpages : la PPL change, la vraisemblance non
  par mot : 2.7144   par sous-mot : 2.1147
…
OK — toutes les vérifications sont passées.
```

### Le même calcul sur un vrai modèle

L'ancienne version de ce fichier calculait la perplexité d'un modèle Hugging Face avec deux défauts. `truncation=True` coupait le texte à la longueur maximale du modèle, sans le dire : N n'était plus la longueur du document. Et les morceaux successifs ne se recouvraient pas : le premier token de chaque morceau était prédit sans aucun contexte, ce qui gonfle la perplexité. La version ci-dessous fait glisser une fenêtre : chaque token est noté une seule fois, avec jusqu'à `max_length` tokens de contexte. Elle n'est pas exécutée par le harnais.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`calculer_perplexite(model, tokenizer, texte, max_length, stride)`** — Cette fonction lit un long document comme un correcteur qui avance une règle sur la page, en ne notant chaque mot qu'une fois mais en gardant sous les yeux les lignes qui précèdent : elle reçoit un modèle de langue, son tokenizer, le texte, la largeur de fenêtre `max_length` (512 par défaut) et le pas `stride` (256 par défaut), met le modèle en mode évaluation, découpe tout le texte en identifiants sans troncature, puis fait glisser une fenêtre de pas en pas. Dans chaque fenêtre, elle masque par la valeur −100 les tokens déjà notés, qui ne servent plus que de contexte, demande au modèle la perte moyenne sur les autres, la multiplie par leur nombre pour retrouver une somme, et cumule sommes et effectifs jusqu'à la fin du texte. Elle renvoie l'exponentielle de la somme des −ln p divisée par le nombre de tokens notés, exactement la forme logarithmique de la perplexité du programme précédent, appliquée cette fois à un vrai modèle.

```python
# [extrait] — PyTorch + transformers, non exécuté par le harnais (pip install torch transformers)
import math

import torch


def calculer_perplexite(model, tokenizer, texte, max_length=512, stride=256):
    """Fenêtre glissante : chaque token est noté une fois, avec jusqu'à max_length tokens de contexte."""
    model.eval()                                          # coupe le dropout : même texte, même résultat
    input_ids = tokenizer(texte, return_tensors="pt").input_ids   # pas de truncation : tout le texte
    somme_nll, n_notes, fin_precedente = 0.0, 0, 0
    for debut in range(0, input_ids.size(1), stride):
        fin = min(debut + max_length, input_ids.size(1))
        a_noter = fin - fin_precedente                    # tokens pas encore notés par une fenêtre précédente
        morceau = input_ids[:, debut:fin]
        labels = morceau.clone()
        labels[:, :-a_noter] = -100                       # -100 : sert de contexte, n'est pas noté
        with torch.no_grad():
            perte = model(morceau, labels=labels).loss    # moyenne des −ln p sur les tokens notés
        n = (labels[:, 1:] != -100).sum().item()          # le modèle décale d'un cran : le 1er token n'a pas de prédiction
        somme_nll += perte.item() * n                     # on repasse de la moyenne à la somme
        n_notes += n
        fin_precedente = fin
        if fin == input_ids.size(1):
            break
    return math.exp(somme_nll / n_notes)
```

`model(morceau, labels=labels).loss` est déjà la moyenne des −ln p sur les tokens notés : la multiplier par leur nombre redonne une somme, qu'on peut additionner d'une fenêtre à l'autre même si les fenêtres n'ont pas la même taille. À la fin, `math.exp(somme_nll / n_notes)` est exactement la forme logarithmique de la formule.

## Squelette algorithmique

Trois algorithmes : la perplexité à partir des probabilités des tokens réels, le modèle bigramme qui fournit ces probabilités dans le programme, et la fenêtre glissante qui les obtient d'un vrai LLM sur un long texte.

### Perplexité, forme logarithmique

Entrée : la liste des N probabilités que le modèle donnait aux tokens réels. Sortie : la perplexité, infinie si un token réel était impossible, indéfinie s'il n'y a aucun token. L'idée : additionner des logarithmes au lieu de multiplier des probabilités, puis repasser à l'exponentielle une seule fois, à la fin.

```text
ALGORITHME Perplexite
ENTRÉE : p[1..N], probabilités des tokens réels
SORTIE : PPL ∈ [1, ∞] ou INDÉFINI
  SI N = 0 ALORS
    RETOURNER INDÉFINI
  FIN SI
  somme_log ← 0
  POUR i DE 1 À N FAIRE
    SI p[i] < 0 OU p[i] > 1 ALORS
      SIGNALER UNE ERREUR « ce n'est pas une probabilité »
    FIN SI
    SI p[i] = 0 ALORS
      RETOURNER ∞                                    (le modèle avait exclu le token réel)
    FIN SI
    somme_log ← somme_log + ln p[i]
  FIN POUR
  RETOURNER exp(− somme_log / N)
```

**Complexité :** O(N) en temps, parce que chaque probabilité coûte une vérification et un logarithme ; l'exponentielle finale coûte O(1). La mémoire supplémentaire est en O(1) : un seul accumulateur, qui reste de taille modeste (environ −2,3 par token à 0,1) alors que le produit des probabilités sous-déborde dès 324 tokens.

**Du squelette au code :** le test N = 0 est `if not probas: return None` ; la boucle est la boucle `for p in probas` de `perplexite`, avec la garde `if not 0.0 <= p <= 1.0`, le retour `math.inf` et l'accumulation `somme_log += math.log(p)` ; le retour est `math.exp(-somme_log / len(probas))`. `perplexite_produit` est la version qui multiplie au lieu d'additionner, gardée dans le programme pour montrer son échec.

### Modèle bigramme lissé : entraîner, puis noter un texte

Entrées : un corpus de phrases, un vocabulaire V, puis une phrase à noter. Sortie : la liste des probabilités des tokens de la phrase, prête pour l'algorithme précédent. L'idée : compter les passages d'un mot au suivant, puis ajouter 1 à chaque compte (lissage de Laplace) pour qu'aucun mot du vocabulaire n'ait une probabilité nulle.

```text
ALGORITHME BigrammeLaplace
ENTRÉES : corpus (liste de phrases), vocabulaire V, phrase à noter w[1..N]
SORTIE : p[1..N]
  c ← compteur vide de couples ; c_ctx ← compteur vide de mots
  POUR chaque phrase du corpus FAIRE
    jetons ← [<s>] suivi des mots de la phrase
    POUR chaque couple consécutif (a, b) de jetons FAIRE
      SI b ∉ V ALORS SIGNALER UNE ERREUR « mot hors vocabulaire » FIN SI
      c[(a, b)] ← c[(a, b)] + 1
      c_ctx[a] ← c_ctx[a] + 1
    FIN POUR
  FIN POUR
  précédent ← <s>
  POUR i DE 1 À N FAIRE
    p[i] ← (c[(précédent, w[i])] + 1) / (c_ctx[précédent] + |V|)
    précédent ← w[i]
  FIN POUR
  RETOURNER p
```

**Complexité :** l'entraînement coûte O(T) en temps pour un corpus de T tokens, parce que chaque couple consécutif fait deux mises à jour de compteur en O(1) en moyenne ; la mémoire est en O(B), où B est le nombre de couples distincts rencontrés, au plus min(T, |V|²). Noter une phrase de N tokens coûte O(N) consultations. Dans le programme, le test `mot not in self.vocab` parcourt une liste triée et coûte O(|V|) à chaque appel : un `set` le ramènerait à O(1), ce qui compte dès que le vocabulaire dépasse quelques milliers de mots.

**Du squelette au code :** les deux boucles d'entraînement sont `Bigramme.__init__`, avec `self.comptes[(a, b)] += 1` et `self.contextes[a] += 1` ; la formule de Laplace est `Bigramme.proba` ; la boucle de notation est `probas_du_texte`, qui fabrique les couples avec `zip(jetons, jetons[1:])` au lieu de tenir une variable `précédent`.

### Fenêtre glissante sur un vrai modèle

Entrées : la suite des identifiants de tokens d'un texte de longueur L, la longueur de contexte maximale M du modèle et un pas S ≤ M. Sortie : la perplexité du texte entier. L'idée : chaque fenêtre de M tokens ne note que les tokens qu'aucune fenêtre précédente n'a notés ; les autres servent seulement de contexte, pour que chaque token soit prédit avec le plus de passé possible.

```text
ALGORITHME PerplexiteFenetreGlissante
ENTRÉES : ids[1..L], M, S
SORTIE : PPL
  somme_nll ← 0 ; n_notés ← 0 ; fin_précédente ← 0 ; début ← 0
  TANT QUE début < L FAIRE
    fin ← min(début + M, L)
    à_noter ← fin − fin_précédente
    fenêtre ← ids[début .. fin]
    marquer comme « contexte seulement » tous les tokens de la fenêtre sauf les à_noter derniers
    perte ← modèle(fenêtre)                      (moyenne des −ln p sur les tokens notés)
    n ← nombre de tokens notés                    (le premier token d'une fenêtre n'a pas de prédiction)
    somme_nll ← somme_nll + perte · n
    n_notés ← n_notés + n
    fin_précédente ← fin
    SI fin = L ALORS
      RETOURNER exp(somme_nll / n_notés)
    FIN SI
    début ← début + S
  FIN TANT QUE
```

**Complexité :** environ L / S fenêtres, chacune coûte un passage du modèle sur M tokens, soit O((L / S) · M) tokens traités ; un pas S plus petit donne plus de contexte à chaque token mais multiplie le calcul. La mémoire est celle d'une fenêtre, O(M) tokens et les activations du modèle, indépendante de L.

**Du squelette au code :** cet algorithme est la fonction `calculer_perplexite` de l'extrait PyTorch ci-dessus, qui n'est pas exécutée par le harnais. La boucle `TANT QUE` est le `for debut in range(0, input_ids.size(1), stride)` suivi du `break` ; le marquage « contexte seulement » est `labels[:, :-a_noter] = -100` ; le comptage des tokens notés est `(labels[:, 1:] != -100).sum()`. Le calcul final `exp(somme_nll / n_notés)` est la même forme logarithmique que `perplexite` dans le bloc exécutable.

## Cas d'usage réels aux Émirats

Les perplexités et les seuils ci-dessous sont illustratifs : ils dépendent du modèle, du tokenizer et du jeu de test.

### Assurance — mesurer l'adaptation d'un modèle aux notes de sinistre

Un assureur auto et santé adapte un modèle open source à ses notes de gestionnaires de sinistres, écrites en anglais avec des termes arabes translittérés (noms de quartiers, de garages, d'hôpitaux). Il garde à part 2 000 notes jamais vues à l'entraînement et mesure la perplexité avant et après l'adaptation : par exemple 18,4 avant et 9,7 après, soit ΔPPL = 8,7 positif. Il mesure aussi la perplexité sur un jeu de textes généraux, pour vérifier que le modèle n'a pas « oublié » le reste en se spécialisant ; si celle-ci monte fortement, l'adaptation a abîmé le modèle. Sans ce double contrôle, l'équipe aurait célébré un modèle excellent sur les notes et mauvais pour rédiger un courrier au client. La perplexité ne suffit pas pour décider la mise en production : les métriques de tâche (fidélité, étape 54 ; justesse, étape 63) restent le juge final. On suit les deux perplexités à chaque nouvelle version, sur des jeux de test figés.

### Secteur public — comparer deux modèles arabes sans se tromper d'unité

Une entité de services publics en ligne, accessible par UAE Pass, choisit le modèle de son assistant bilingue arabe et anglais et hésite entre deux familles de modèles arabes, Jais et Falcon par exemple. Leurs tokenizers découpent l'arabe très différemment : l'un peut produire deux fois plus de tokens que l'autre pour la même phrase. Comparer leurs perplexités par token reviendrait à comparer des kilomètres et des miles, comme le montre la démonstration (point 8) : 2,7144 par mot contre 2,1147 par sous-mot pour la même probabilité de phrase. L'équipe calcule donc la log-vraisemblance totale de chaque modèle sur le même jeu de demandes réelles anonymisées (PDPL), puis la ramène au mot ou au caractère. Sans cette précaution, elle aurait choisi le modèle au tokenizer le plus fin, pas le meilleur modèle. Le choix final s'appuie sur la perplexité normalisée et sur un jeu d'évaluation de tâches (étape 13 bis).

### RH — repérer les documents illisibles avant de les indexer

Un cabinet RH multi-émirats indexe dans un RAG les documents fournis par les candidats : contrats, attestations, diplômes scannés. Certains passent par un OCR qui produit du charabia (colonnes mélangées, arabe lu de gauche à droite). Un petit modèle de langue de référence calcule la perplexité de chaque page extraite ; une page normale reste autour d'une valeur typique, une page d'OCR raté dépasse de loin le 99e percentile des pages saines du mois précédent. Ces pages partent en revue humaine au lieu d'être indexées, parce qu'un passage illisible injecté dans le contexte fait halluciner l'agent sur la date d'expiration d'un visa ou le montant d'un salaire. Le seuil est un percentile mesuré, pas une constante universelle : il se recalcule quand l'OCR ou le modèle change. On suit la part de pages écartées et le taux de réponses de l'agent corrigées par l'équipe sur ces dossiers.

### Banque — détecter une dérive du vocabulaire des clients

Une banque de détail de Dubaï calcule chaque semaine la perplexité moyenne des messages reçus par son assistant de messagerie, sous le modèle qui a servi à construire ses intentions et sa base de réponses. Une hausse durable signale que les clients parlent autrement : nouveau produit de finance islamique, campagne de fraude par SMS qui fait arriver un vocabulaire inconnu, ou messages en arabizi (arabe écrit en lettres latines et en chiffres). L'équipe ne bloque rien sur ce signal ; elle échantillonne les messages les plus surprenants, les fait lire par un analyste et enrichit la base documentaire du RAG ou le jeu d'évaluation. Sans ce signal, l'assistant aurait continué à mal router une nouvelle famille de demandes pendant des semaines. Une perplexité moyenne masque une queue de distribution : l'équipe suit aussi le 95e percentile (fonction `p95` du guide) de la perplexité par message.

### Immobilier — encadrer les descriptions d'annonces générées

Une agence de Dubaï génère les descriptions de ses annonces (surface en sqft, quartier, charges, statut off-plan) avec un LLM, puis les contrôle avant publication. Une description dont la perplexité sous le modèle de l'agence est anormalement haute contient souvent des mots incohérents ou un mélange de langues ; une description dont la perplexité est anormalement **basse** est souvent une boucle de répétition (« vue sur la marina, vue sur la marina… »), que le modèle trouve très prévisible. L'agence encadre donc la perplexité par une bande basse et une bande haute, calibrées sur les annonces validées. Sans la borne basse, les répétitions passeraient le contrôle, puisqu'elles ont l'air « sûres ». La vérification des faits (surface, prix en AED) reste faite par un contrôle de fidélité aux données du bien (étape 54), que la perplexité ne remplace pas.

### Crypto — une faible perplexité n'est pas une preuve de vérité

Une plateforme d'actifs virtuels agréée par la VARA envisage d'utiliser la perplexité des réponses de son agent comme indice de confiance : « si le modèle était peu surpris par sa propre réponse, elle est fiable ». L'équipe teste l'idée sur un jeu de questions sur les frais de retrait et les délais de règlement, dont les réponses sont connues. Le résultat est décevant : des réponses fausses mais formulées comme les réponses habituelles ont une perplexité aussi basse que les bonnes, parce que la perplexité mesure la ressemblance au style attendu, pas l'exactitude. La température d'échantillonnage déforme aussi la mesure, et l'API utilisée n'expose pas toujours les log-probabilités. La plateforme abandonne l'idée et s'appuie sur la fidélité aux documents récupérés (étape 54) et sur l'évaluation de la justesse (étape 63). On garde la perplexité pour ce qu'elle fait bien : juger un modèle sur un corpus, et repérer des textes inhabituels.

## Pièges et limites

- **Écrire « PPL ≤ |V| ».** C'est faux dès que le modèle est sûr de lui et se trompe ; seule l'entropie propre d'une distribution vérifie exp(H(Q)) ≤ |V|.
- **Comparer des perplexités entre tokenizers différents.** On compare la log-vraisemblance du même texte, normalisée par mot ou par caractère.
- **Calculer la forme produit.** Le produit des probabilités vaut 0 dès 324 tokens à 0,1 ; on additionne des logarithmes.
- **Lire ΔPPL à l'envers.** Avant moins après, positif = amélioration.
- **Prendre une faible perplexité pour une garantie.** Une hallucination fluide et une boucle de répétition ont une perplexité basse ; la perplexité ne remplace ni la fidélité ni la justesse.

### Exercice feuille blanche

1. Sans regarder le code, écrire `perplexite` avec ses trois cas limites, puis vérifier que [0,25 ; 0,25 ; 0,25 ; 0,25] donne 4 et [0,8 ; 0,5] donne √2,5 ≈ 1,581.
2. Prédire, puis vérifier : un modèle donne 0,9 au token réel pendant 9 tokens, puis 0,001 au dixième. Que vaut sa perplexité ? (Réponse : exp((−9 ln 0,9 − ln 0,001)/10) ≈ 2,19 : un seul token très surprenant suffit à doubler la perplexité.)
3. Trouver le bug : `return math.exp(-somme_log)`, sans division par `len(probas)`. Que donne cette variante sur [0,5 ; 0,25 ; 0,125], et que devrait-elle donner ? (Réponse : 64 au lieu de 4 ; c'est l'erreur corrigée à l'étape 62.)

## Pour aller plus loin

- Les bits par caractère et les bits par octet ramènent la log-vraisemblance à une unité indépendante du tokenizer.
- La perplexité conditionnelle d'une réponse sachant la question sert parfois à classer des réponses candidates ; elle hérite des mêmes limites.
- La version métier de cette formule, avec ses pièges en production, est à l'étape 62.

> Suite : [Évaluation : formules, théorèmes et algorithmes](<53-Evaluation-Formules-Theoremes-Algorithmes.md>) — étape 53.
