# Étape 54 — Évaluation — Faithfulness

> Étape 54 du parcours · Prérequis : [Évaluation : formules, théorèmes et algorithmes](<53-Evaluation-Formules-Theoremes-Algorithmes.md>) · Suite : [Answer Relevancy](<55-Evaluation-Formule-Answer-Relevancy.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 54-Evaluation-Formule-Faithfulness.md

## Définition

La Faithfulness (fidélité) mesure la proportion des affirmations de la réponse générée qui sont réellement justifiées par le contexte récupéré. On découpe la réponse en affirmations atomiques, des phrases courtes et autonomes comme « le plafond est de 5 000 AED », puis un juge, humain ou LLM, décide pour chacune si elle se déduit du contexte. Le score est la part des affirmations justifiées : 1 veut dire qu'aucune n'est inventée, 0 que toutes le sont. C'est la métrique anti-hallucination principale d'un RAG. Elle ne dit pas si la réponse est vraie dans le monde, seulement si elle est fidèle aux documents fournis : un document faux, fidèlement recopié, donne un score de 1.

## Rôle dans un agent

La Faithfulness juge l'étape **agir** de la boucle, au moment où l'agent rédige sa réponse à partir des morceaux que le retriever a placés dans son contexte. Elle sert à trois endroits. Hors ligne, sur le jeu de référence, elle alimente la **barrière d'intégration continue** de l'étape 13 bis : une nouvelle version de prompt ou de modèle ne part pas en production si la fidélité baisse. En ligne, un **garde-fou** peut calculer une fidélité approchée avant d'envoyer la réponse et la bloquer si une affirmation chiffrée n'apparaît pas dans le contexte. Enfin, la liste des affirmations rejetées est le meilleur outil de **diagnostic** : elle dit exactement ce que le modèle a inventé, pour qu'un humain corrige le prompt ou la base documentaire.

## Équation complète

Score d'une réponse :

$$
\text{Faithfulness} = \frac{|V|}{|S|} \qquad \text{indéfinie si } |S| = 0
$$

Agrégation sur un jeu de m réponses mesurables, moyenne des ratios (macro) puis ratio des sommes (micro) :

$$
F_{\text{macro}} = \frac{1}{m} \sum_{j=1}^{m} \frac{|V_j|}{|S_j|}
\qquad
F_{\text{micro}} = \frac{\sum_{j} |V_j|}{\sum_{j} |S_j|} = \sum_{j} \frac{|S_j|}{\sum_{l} |S_l|} \cdot \frac{|V_j|}{|S_j|}
$$

Borne basse de Wilson quand les n réponses du jeu sont toutes entièrement fidèles, et taille minimale du jeu pour un seuil τ :

$$
\text{borne basse} = \frac{n}{n + z^2}
\qquad
\frac{n}{n + z^2} \ge \tau \iff n \ge \frac{\tau\, z^2}{1 - \tau}
$$

## Décryptage des symboles

$$
S
$$

**Sens :** l'ensemble des affirmations atomiques extraites de la réponse générée · **Type / plage :** ensemble fini, éventuellement vide · **Variable Python :** `affirmations`, ou la longueur de `verdicts`.

$$
V \subseteq S
$$

**Sens :** les affirmations que le juge déclare déductibles du contexte récupéré · **Type / plage :** sous-ensemble de S, donc 0 ≤ |V| ≤ |S| · **Variable Python :** les `True` de `verdicts`.

$$
|V|,\; |S|
$$

**Sens :** nombre d'affirmations justifiées, nombre total d'affirmations · **Type / plage :** entiers ≥ 0 · **Variable Python :** `sum(1 for v in verdicts if v)` et `len(verdicts)`.

$$
F_{\text{macro}},\; F_{\text{micro}}
$$

**Sens :** fidélité typique d'une réponse (chaque réponse pèse autant) et fidélité par affirmation (chaque affirmation pèse autant) · **Type / plage :** réels dans [0, 1], `None` si aucune réponse n'est mesurable · **Variable Python :** `macro(scores)`, `micro(jeu)`.

$$
z
$$

**Sens :** quantile de la loi normale pour un niveau de confiance de 95 % · **Type / plage :** 1,96, donc z² = 3,8416 · **Variable Python :** `z`.

$$
\tau
$$

**Sens :** seuil métier de la barrière, comparé à la borne basse de Wilson et non au score brut · **Type / plage :** réel dans ]0, 1[, par exemple 0,90 ou 0,95 · **Variable Python :** `seuil`.

## Démonstration

### 1. Le score est entre 0 et 1, et n'existe pas sans affirmation

Comme V est inclus dans S, on a 0 ≤ |V| ≤ |S|. Si |S| > 0, on divise les trois membres par le nombre positif |S|, ce qui ne change pas le sens des inégalités :

$$
0 \le \frac{|V|}{|S|} \le 1
$$

Le score vaut 1 si et seulement si |V| = |S|, c'est-à-dire V = S : chaque affirmation est justifiée. Il vaut 0 si et seulement si V est vide. Si |S| = 0, la réponse n'affirme rien (« je ne peux pas répondre à cette question ») : il n'y a rien à juger, et le score n'est pas 0, ni 1, ni NaN. Le programme renvoie `None`, et cette réponse est comptée à part (point 4).

### 2. Monotonie, et comment on gonfle un score

Notons v = |V| et s = |S|, avec 0 < s. Ajouter une affirmation **justifiée** donne (v + 1)/(s + 1). On compare en multipliant en croix, ce qui est permis parce que les dénominateurs sont positifs :

$$
\frac{v+1}{s+1} \ge \frac{v}{s} \iff s(v+1) \ge v(s+1) \iff s \ge v
$$

ce qui est toujours vrai, avec égalité seulement si v = s (le score valait déjà 1). Ajouter une affirmation **inventée** donne v/(s + 1) ≤ v/s, avec égalité seulement si v = 0. Le score monte quand on ajoute du vrai, baisse quand on ajoute du faux.

Le revers : on peut le gonfler. Ajouter k affirmations triviales mais justifiées (« le contrat est une assurance auto ») donne

$$
\frac{v + k}{s + k} = 1 - \frac{s - v}{s + k} \xrightarrow[k \to \infty]{} 1
$$

Sur l'exemple, 1/3 devient 8/10 = 0,8 avec sept évidences, sans qu'aucune erreur ne soit corrigée. Un prompt qui pousse le modèle à paraphraser le contexte améliore la Faithfulness sans améliorer la réponse : il faut lire la liste des rejets, pas seulement le score.

### 3. Moyenne des ratios contre ratio des sommes

Sur un jeu de réponses, deux agrégats sont possibles. Le ratio des sommes est une moyenne des ratios **pondérée** par le nombre d'affirmations, parce que

$$
\frac{\sum_j |V_j|}{\sum_l |S_l|} = \sum_j \frac{|S_j|}{\sum_l |S_l|}\cdot\frac{|V_j|}{|S_j|}
$$

et les poids |Sⱼ|/∑|Sₗ| sont positifs de somme 1. Les deux agrégats coïncident quand toutes les réponses ont le même nombre d'affirmations, et seulement alors en général. **Contre-exemple chiffré :** la réponse A a 1 affirmation, justifiée (1/1) ; la réponse B en a 9, dont 3 justifiées (3/9). La moyenne des ratios vaut (1 + 0,333)/2 = 0,667 ; le ratio des sommes vaut 4/10 = 0,4, soit 0,1 × 1 + 0,9 × 0,333. Les deux nombres répondent à deux questions différentes : « une réponse typique est-elle fidèle ? » pour le macro, « une affirmation tirée au hasard est-elle fidèle ? » pour le micro. Une longue réponse peu fidèle pèse lourd dans le micro et compte pour une seule réponse dans le macro. On choisit l'un des deux, on l'écrit dans la documentation de la barrière, et on ne compare jamais un macro à un micro.

### 4. Pourquoi None et pas NaN

L'ancien code renvoyait `float('nan')` pour une réponse sans affirmation. La norme IEEE 754 des flottants veut que toute comparaison avec NaN soit fausse : `nan >= 0.9` vaut `False`, mais `nan < 0.9` vaut **aussi** `False`. Une barrière écrite « bloquer si score < seuil » laisse donc passer un NaN, et le déploiement part. Pire, un seul NaN dans une liste rend la moyenne NaN : (0,9 + NaN)/2 = NaN, qui passe à son tour la barrière. La convention du parcours est `None` : la réponse est **indéfinie**, elle n'entre ni dans le macro ni dans le micro, elle est comptée à part, et une barrière sans aucune réponse mesurable **refuse** le déploiement. En Java, le même rôle est tenu par un `OptionalDouble` vide (étape 53).

### 5. Wilson sur le jeu de référence, et la taille minimale du jeu

Pour la barrière, on mesure la proportion de réponses **entièrement fidèles** (score égal à 1) sur le jeu de référence, et l'on compare la borne basse de son intervalle de Wilson au seuil τ, pas la proportion brute. La dérivation de l'intervalle est à l'étape 7, la barrière et la comparaison de deux versions par McNemar à l'étape 13 bis. Avec 46 réponses entièrement fidèles sur 50, la proportion vaut 0,92 mais l'intervalle est [0,8116 ; 0,9685] : pour un seuil de 0,90, la barrière refuse.

**Combien de réponses faut-il au minimum ?** Le meilleur cas est un jeu où les n réponses sont toutes fidèles, p̂ = 1. Dans la formule de Wilson, le terme p̂(1 − p̂)/n s'annule ; le centre vaut (1 + z²/(2n))/(1 + z²/n) et la demi-largeur vaut (z²/(2n))/(1 + z²/n), parce que z·√(z²/(4n²)) = z²/(2n). La borne basse est leur différence :

$$
\frac{1 + \dfrac{z^2}{2n} - \dfrac{z^2}{2n}}{1 + \dfrac{z^2}{n}} = \frac{1}{1 + \dfrac{z^2}{n}} = \frac{n}{n + z^2}
$$

Elle dépasse τ si et seulement si n ≥ τz²/(1 − τ). Pour τ = 0,90 : n ≥ 0,9 × 3,8416 / 0,1 = 34,57, soit 35 réponses. Pour τ = 0,95 : n ≥ 0,95 × 3,8416 / 0,05 = 72,99, soit 73 réponses, et une seule réponse infidèle oblige à en mesurer davantage. Un jeu de 50 réponses ne peut donc **jamais** certifier un seuil de 0,95, même avec un score parfait (borne basse 50/53,84 = 0,9287).

Attention à l'unité : les affirmations d'une même réponse ne sont pas indépendantes (un mauvais morceau récupéré fausse plusieurs affirmations à la fois). Appliquer Wilson au micro, comme si chaque affirmation était un tirage indépendant, donnerait un intervalle trop étroit. On l'applique aux réponses.

### 6. Exemple fait à la main (le code reprend ces nombres)

**Contexte récupéré :** « Plafond dommages parking : 5 000 AED. Franchise standard : 500 AED. Aucune franchise si le véhicule est stationné et le conducteur absent. »

**Réponse :** « Le plafond est de 5 000 AED. La franchise est de 1 000 AED. Aucune franchise ne s'applique. »

1. « Le plafond est de 5 000 AED » : justifiée, elle entre dans V.
2. « La franchise est de 1 000 AED » : inventée, le contexte dit 500 AED.
3. « Aucune franchise ne s'applique » : le contexte pose une condition (véhicule stationné, conducteur absent) que l'affirmation supprime ; elle n'est pas déductible telle quelle.

|S| = 3 et |V| = 1, donc

$$
\text{Faithfulness} = \frac{1}{3} \approx 0{,}333
$$

Sur trois affirmations, deux sont inventées ou déformées. Dans un contexte d'assurance ou de RH, on ne laisse pas l'agent répondre seul : on corrige le prompt, on vérifie les morceaux récupérés, ou l'on ajoute un garde-fou qui compare les montants de la réponse à ceux du contexte. Avec une affirmation justifiée de plus, le score monte à 2/4 = 0,5 ; avec une inventée de plus, il descend à 1/4 = 0,25 (point 2).

## Effets et comportement

- **Plus |V| augmente à |S| fixé**, plus le score augmente : la réponse est plus fiable.
- **Plus |S| augmente sans que |V| suive** (des affirmations ajoutées et non justifiées), plus le score baisse : le modèle invente davantage.
- **Ajouter des évidences justifiées gonfle le score** vers 1 sans corriger aucune erreur (démonstration, point 2).
- **Un score qui passe de 0,95 à 0,70** après un changement de prompt signifie que le modèle invente davantage ; on bloque le déploiement, après avoir vérifié que l'écart dépasse le bruit du juge (étape 53, point 6).

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| \|V\| / \|S\| | `faithfulness(verdicts)` |
| le juge | `JugeScripte.est_supportee(affirmation, contexte)` |
| score et rejets d'une réponse | `faithfulness_reponse(affirmations, contexte, juge)` |
| F_macro | `macro(scores)` |
| F_micro | `micro(jeu)` |
| intervalle de Wilson | `wilson(succes, n, z)` (code canonique, étape 7) |
| n ≥ τz²/(1 − τ) | `n_minimum(seuil)` |
| barrière | `barriere(scores, seuil)` |

### Déroulé, ligne par ligne

**`faithfulness(verdicts)`** reçoit un booléen par affirmation. `if not verdicts: return None` traite la réponse qui n'affirme rien : ni zéro, ni NaN, une absence de mesure. Ensuite, `sum(1 for v in verdicts if v)` compte |V| et la division par `len(verdicts)` donne |V|/|S|. Pour `[True, False, False]`, cela fait 1/3.

**`JugeScripte`** joue le rôle du port « juge » de l'architecture hexagonale : en production, ce serait un adaptateur qui appelle un LLM avec le contexte et l'affirmation ; ici, un dictionnaire de verdicts écrits d'avance, comme le faux LLM scripté du parcours. Le compteur `appels` permet de vérifier que chaque affirmation est jugée une fois, et une affirmation absente du dictionnaire lève `ValueError` au lieu d'être déclarée fidèle par défaut.

**`faithfulness_reponse(affirmations, contexte, juge)`** appelle le juge sur chaque affirmation, construit la liste des rejets avec `zip(affirmations, verdicts)`, puis renvoie le score et cette liste. Sur l'exemple, le juge est appelé trois fois, le score vaut 0,333, et les rejets sont « La franchise est de 1 000 AED » et « Aucune franchise ne s'applique ».

**`macro(scores)`** filtre les `None` avant de moyenner ; sans réponse mesurable, il renvoie `None`. **`micro(jeu)`** additionne les longueurs de toutes les listes de verdicts (les réponses vides ajoutent 0) et divise le nombre total de `True` par ce total. Sur le jeu `[[True], [True, True, True, False, …], []]`, `macro` vaut (1 + 1/3)/2 = 0,667 et `micro` vaut 4/10 = 0,4.

**`wilson(succes, n, z)`** est la fonction canonique du parcours : `None` pour n = 0, `ValueError` si le nombre de succès sort de [0, n], puis le centre et la demi-largeur. Pour 46 sur 50 : p = 0,92, d = 1,076832, centre 0,89003, demi-largeur 0,07842, intervalle [0,8116 ; 0,9685].

**`n_minimum(seuil)`** calcule `ceil(seuil * z * z / (1 - seuil))`. Le `- 1e-9` évite qu'un arrondi flottant juste au-dessus d'un entier fasse sauter d'une unité : 34,57 donne 35, 72,99 donne 73.

**`barriere(scores, seuil)`** garde les scores mesurables, refuse s'il n'y en a aucun, compte les réponses entièrement fidèles (`s == 1.0`), calcule l'intervalle de Wilson et accepte seulement si la borne basse atteint le seuil. Le message rend la décision lisible dans un journal d'intégration continue.

**`main()`**, bloc par bloc.

1. La réponse sur la franchise : score 1/3, trois appels au juge, deux rejets.
2. Une affirmation justifiée de plus (0,5), une inventée de plus (0,25), sept évidences de plus (0,8).
3. Le jeu de trois réponses : 1,0, 0,333 et `None` ; macro 0,667, micro 0,4, une réponse indéfinie. L'`assert` vérifie aussi que le micro est la moyenne pondérée par |S| : 0,1 × 1 + 0,9 × 1/3.
4. Les comparaisons avec NaN, la barrière naïve qui laisse passer NaN, et la vraie barrière qui refuse une liste de `None`.
5. Le jeu de 50 réponses (46 entièrement fidèles) refusé au seuil 0,90 ; les tailles minimales 35 et 73, vérifiées dans les deux sens (n suffit, n − 1 ne suffit pas) ; un jeu de 73 réponses parfaites accepté au seuil 0,95. Enfin, une affirmation inconnue du juge scripté doit lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`faithfulness(verdicts)`** — Cette fonction est le vérificateur de faits qui, la réponse découpée en affirmations, coche celles que le contexte justifie : elle reçoit la liste des verdicts du juge, un booléen par affirmation, renvoie `None` si la liste est vide, parce qu'une réponse qui n'affirme rien n'a pas de score, et sinon divise le nombre de verdicts vrais |V| par le nombre total d'affirmations |S|. Elle renvoie ce taux, 1/3 pour la réponse sur la franchise, 0,5 avec une affirmation justifiée de plus, 0,25 avec une affirmation inventée de plus et 0,8 quand on y ajoute sept évidences, ce qui montre qu'on peut gonfler le score sans corriger aucune erreur.

**`JugeScripte.__init__(verdicts)`** — Le constructeur prépare un juge de théâtre qui connaît son texte par cœur : il reçoit un dictionnaire qui associe chaque affirmation au verdict écrit d'avance, vrai si le contexte la soutient, faux sinon, le range dans l'attribut `verdicts` et met à zéro le compteur `appels`. Il ne renvoie rien ; ce juge tient la place du LLM qu'un adaptateur appellerait en production, et le compteur permet à `main` de vérifier que la réponse sur la franchise a demandé exactement trois jugements, un par affirmation.

**`JugeScripte.est_supportee(affirmation, contexte)`** — Cette méthode est l'instant où le juge lève les yeux de son pupitre et rend son verdict : elle reçoit une affirmation et le contexte récupéré, augmente d'abord de un le compteur d'appels, puis cherche l'affirmation dans son dictionnaire et renvoie le booléen prévu. Le contexte n'est pas lu, puisque tout est écrit d'avance ; en revanche, une affirmation absente du dictionnaire lève une `ValueError` au lieu d'être déclarée fidèle par défaut, et `main` le vérifie à la fin avec une « Affirmation imprévue ».

**`micro(jeu)`** — Cette fonction est le comptable qui verse toutes les affirmations du jeu dans un seul grand registre avant de calculer un taux, au lieu de faire la moyenne des taux réponse par réponse : elle reçoit la liste des listes de verdicts, une par réponse, additionne leurs longueurs, et renvoie le nombre total de verdicts vrais divisé par ce total, ou `None` si le jeu ne contient aucune affirmation. Une réponse vide n'y ajoute rien, et chaque affirmation pèse autant : sur le jeu à trois réponses, 4 affirmations soutenues sur 10 donnent 0,4, alors que la moyenne macro des scores par réponse vaut 0,667.

**`n_minimum(seuil, z)`** — Celle-ci répond à la question de l'organisateur d'un examen : combien de copies parfaites faut-il au minimum pour que la borne basse de Wilson atteigne le seuil exigé ? Elle reçoit ce seuil et le quantile z, 1,96 par défaut, calcule seuil × z² ÷ (1 − seuil), retranche 10⁻⁹ pour qu'un résultat tombé pile sur un entier ne soit pas poussé d'une unité par un arrondi flottant, et renvoie l'entier supérieur. Elle donne 35 réponses au seuil 0,90 et 73 au seuil 0,95, et `main` vérifie dans les deux sens que ce nombre suffit et que le nombre précédent ne suffit pas.

**`main()`** — C'est le chef d'orchestre des cinq démonstrations : il fait juger la réponse sur la franchise par le juge scripté, avec un score de 1/3, trois appels et deux rejets, montre ensuite la monotonie du score et la façon de le gonfler avec des évidences, puis agrège un jeu de trois réponses, où la moyenne des ratios vaut 0,667 et le ratio des sommes 0,4. Il prouve ensuite qu'un NaN traverse une barrière naïve parce que toutes ses comparaisons sont fausses, alors que la vraie barrière refuse une liste de `None`, refuse le jeu de 46 réponses fidèles sur 50 au seuil 0,90, calcule les tailles minimales 35 et 73 et accepte 73 réponses parfaites au seuil 0,95 ; une affirmation inconnue doit enfin lever `ValueError` avant le « OK » final.

```python
"""Étape 54 — Faithfulness : score d'une réponse, monotonie, micro contre macro, NaN contre None, Wilson et barrière."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def faithfulness(verdicts: list[bool]) -> float | None:
    """|V| / |S|. None si la réponse n'affirme rien : le score n'existe pas (pas de NaN)."""
    if not verdicts:
        return None
    return sum(1 for v in verdicts if v) / len(verdicts)


class JugeScripte:
    """Port « juge » : en production un LLM ; ici des verdicts écrits d'avance, comme le FakeLLM du parcours."""

    def __init__(self, verdicts: dict[str, bool]):
        self.verdicts = verdicts
        self.appels = 0

    def est_supportee(self, affirmation: str, contexte: str) -> bool:
        self.appels += 1
        if affirmation not in self.verdicts:
            raise ValueError(f"affirmation inconnue du juge scripté : {affirmation}")
        return self.verdicts[affirmation]


def faithfulness_reponse(affirmations: list[str], contexte: str, juge) -> tuple[float | None, list[str]]:
    """Juge chaque affirmation contre le contexte ; renvoie le score et les affirmations rejetées."""
    verdicts = [juge.est_supportee(a, contexte) for a in affirmations]
    rejetees = [a for a, v in zip(affirmations, verdicts) if not v]
    return faithfulness(verdicts), rejetees


def macro(scores: list[float | None]) -> float | None:
    """Moyenne des scores par réponse ; les None (réponses sans affirmation) n'entrent pas dans la moyenne."""
    mesures = [s for s in scores if s is not None]
    return sum(mesures) / len(mesures) if mesures else None


def micro(jeu: list[list[bool]]) -> float | None:
    """Σ|V| / Σ|S| sur tout le jeu : chaque affirmation pèse autant."""
    total = sum(len(v) for v in jeu)
    return sum(sum(1 for x in v if x) for v in jeu) / total if total else None


def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0 (code canonique, étape 7)."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def n_minimum(seuil: float, z: float = 1.96) -> int:
    """Plus petit n pour lequel n réponses toutes fidèles donnent une borne basse ≥ seuil : n/(n + z²) ≥ seuil."""
    return math.ceil(seuil * z * z / (1 - seuil) - 1e-9)


def barriere(scores: list[float | None], seuil: float) -> tuple[bool, str]:
    """Barrière CI : borne basse de Wilson du taux de réponses entièrement fidèles ≥ seuil (étape 13 bis)."""
    mesures = [s for s in scores if s is not None]
    if not mesures:
        return False, "refusé : aucune réponse mesurable"
    fideles = sum(1 for s in mesures if s == 1.0)
    bas, haut = wilson(fideles, len(mesures))
    ok = bas >= seuil
    return ok, f"{'accepté' if ok else 'refusé'} : {fideles}/{len(mesures)} fidèles, Wilson [{bas:.4f} ; {haut:.4f}]"


def main() -> None:
    print("1. La réponse sur la franchise, jugée affirmation par affirmation")
    contexte = ("Plafond dommages parking : 5 000 AED. Franchise standard : 500 AED. "
                "Aucune franchise si le véhicule est stationné et le conducteur absent.")
    affirmations = ["Le plafond est de 5 000 AED", "La franchise est de 1 000 AED", "Aucune franchise ne s'applique"]
    juge = JugeScripte({affirmations[0]: True, affirmations[1]: False, affirmations[2]: False})
    score, rejetees = faithfulness_reponse(affirmations, contexte, juge)
    print(f"  Faithfulness = {score:.3f}   appels au juge = {juge.appels}")
    print(f"  rejetées : {rejetees}")
    assert abs(score - 1 / 3) < 1e-12 and juge.appels == 3 and len(rejetees) == 2

    print("2. Monotonie, et le score qu'on gonfle avec des évidences")
    base = [True, False, False]
    plus_vraie, plus_fausse = faithfulness(base + [True]), faithfulness(base + [False])
    gonflee = faithfulness(base + [True] * 7)
    print(f"  +1 justifiée : {plus_vraie:.3f}   +1 inventée : {plus_fausse:.3f}   +7 évidences : {gonflee:.3f}")
    assert plus_vraie > score > plus_fausse and gonflee == 0.8

    print("3. Agréger un jeu : moyenne des ratios contre ratio des sommes")
    jeu = [[True], [True, True, True] + [False] * 6, []]       # 1/1, 3/9, et une réponse sans affirmation
    scores = [faithfulness(v) for v in jeu]
    print(f"  scores par réponse = {[None if s is None else round(s, 3) for s in scores]}")
    print(f"  macro = {macro(scores):.3f}   micro = {micro(jeu):.3f}   indéfinies = {scores.count(None)}")
    assert round(macro(scores), 3) == 0.667 and micro(jeu) == 0.4
    poids = [len(v) / 10 for v in jeu[:2]]                       # micro = moyenne pondérée par |S|
    assert abs(micro(jeu) - sum(w * s for w, s in zip(poids, scores[:2]))) < 1e-12

    print("4. NaN dans une barrière : toutes les comparaisons sont fausses")
    nan = float("nan")
    print(f"  nan >= 0.9 : {nan >= 0.9}   nan < 0.9 : {nan < 0.9}   moyenne avec un nan : {(0.9 + nan) / 2}")
    barriere_naive = "bloqué" if nan < 0.9 else "déployé"
    print(f"  barrière « bloquer si score < 0.9 » sur nan → {barriere_naive}")
    assert (nan >= 0.9) is False and (nan < 0.9) is False and barriere_naive == "déployé"
    assert barriere([None, None], 0.9) == (False, "refusé : aucune réponse mesurable")

    print("5. Wilson sur le jeu de référence")
    resultats = [1.0] * 46 + [0.5] * 4                           # 46 réponses entièrement fidèles sur 50
    ok, message = barriere(resultats, 0.90)
    print(f"  seuil 0.90 : {message}")
    assert not ok and [round(x, 4) for x in wilson(46, 50)] == [0.8116, 0.9685]
    for seuil in (0.90, 0.95):
        n = n_minimum(seuil)
        print(f"  seuil {seuil:.2f} : il faut au moins {n} réponses, toutes fidèles (borne basse {wilson(n, n)[0]:.4f})")
        assert wilson(n, n)[0] >= seuil > wilson(n - 1, n - 1)[0]
    assert (n_minimum(0.90), n_minimum(0.95)) == (35, 73)
    ok73, message73 = barriere([1.0] * 73, 0.95)
    print(f"  seuil 0.95 : {message73}")
    assert ok73

    try:
        faithfulness_reponse(["Affirmation imprévue"], contexte, juge)
    except ValueError:
        pass
    else:
        raise AssertionError("une affirmation inconnue du juge scripté aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. La réponse sur la franchise, jugée affirmation par affirmation
  Faithfulness = 0.333   appels au juge = 3
  rejetées : ['La franchise est de 1 000 AED', "Aucune franchise ne s'applique"]
2. Monotonie, et le score qu'on gonfle avec des évidences
  +1 justifiée : 0.500   +1 inventée : 0.250   +7 évidences : 0.800
3. Agréger un jeu : moyenne des ratios contre ratio des sommes
  scores par réponse = [1.0, 0.333, None]
  macro = 0.667   micro = 0.400   indéfinies = 1
4. NaN dans une barrière : toutes les comparaisons sont fausses
  nan >= 0.9 : False   nan < 0.9 : False   moyenne avec un nan : nan
  barrière « bloquer si score < 0.9 » sur nan → déployé
5. Wilson sur le jeu de référence
  seuil 0.90 : refusé : 46/50 fidèles, Wilson [0.8116 ; 0.9685]
  seuil 0.90 : il faut au moins 35 réponses, toutes fidèles (borne basse 0.9011)
  seuil 0.95 : il faut au moins 73 réponses, toutes fidèles (borne basse 0.9500)
  seuil 0.95 : accepté : 73/73 fidèles, Wilson [0.9500 ; 1.0000]
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Deux algorithmes : le score d'une réponse, qui appelle le juge, et la décision de la barrière sur tout le jeu de référence, qui ne fait plus que compter.

### Faithfulness d'une réponse

Entrées : la liste des affirmations extraites de la réponse, le contexte récupéré, et un juge qui répond oui ou non pour une affirmation. Sorties : le score, ou « indéfini », et la liste des affirmations rejetées. L'idée : un appel au juge par affirmation, un compteur, et une liste de rejets pour l'analyse humaine.

```text
ALGORITHME FaithfulnessReponse
ENTRÉES : S (liste d'affirmations), contexte, juge
SORTIE : score ∈ [0, 1] ou INDÉFINI, rejetées
  rejetées ← liste vide
  SI |S| = 0 ALORS
    RETOURNER INDÉFINI, rejetées
  FIN SI
  nb_justifiées ← 0
  POUR chaque affirmation a de S FAIRE
    SI juge.est_supportée(a, contexte) ALORS
      nb_justifiées ← nb_justifiées + 1
    SINON
      ajouter a à rejetées
    FIN SI
  FIN POUR
  RETOURNER nb_justifiées / |S|, rejetées
```

**Complexité :** |S| appels au juge, ou un seul si on lui envoie toutes les affirmations en lot : c'est ce coût, en latence et en tokens, qui domine, pas le comptage. Le reste est en O(|S|) en temps et en O(|S|) en mémoire pour la liste des rejets.

**Du squelette au code :** l'appel au juge est `juge.est_supportee(a, contexte)`, fait dans la liste en compréhension de `faithfulness_reponse` ; les rejets sont construits ensuite par `[a for a, v in zip(affirmations, verdicts) if not v]` ; le test |S| = 0 et la division sont dans `faithfulness`, appelée sur la liste des verdicts.

### Agrégation du jeu et barrière d'intégration continue

Entrées : les scores des réponses du jeu de référence, `None` compris, et le seuil τ. Sorties : la décision (accepté ou refusé) et un message. L'idée : écarter les réponses indéfinies sans les oublier, compter les réponses entièrement fidèles, comparer la borne basse de Wilson au seuil.

```text
ALGORITHME BarriereFaithfulness
ENTRÉES : scores[1..m] (réels ou INDÉFINI), seuil τ, z = 1,96
SORTIE : décision, message
  mesures ← les scores qui ne valent pas INDÉFINI
  SI |mesures| = 0 ALORS
    RETOURNER refusé, « aucune réponse mesurable »
  FIN SI
  fidèles ← 0
  POUR chaque score s de mesures FAIRE
    SI s = 1 ALORS
      fidèles ← fidèles + 1
    FIN SI
  FIN POUR
  (bas, haut) ← Wilson(fidèles, |mesures|, z)
  SI bas ≥ τ ALORS
    RETOURNER accepté, (fidèles, |mesures|, bas, haut)
  SINON
    RETOURNER refusé, (fidèles, |mesures|, bas, haut)
  FIN SI
```

**Complexité :** O(m) en temps, parce que le filtrage et le comptage parcourent chacun les m scores une fois et que l'intervalle de Wilson coûte O(1). La mémoire est en O(m) pour la liste filtrée, ou O(1) si l'on compte au fil de l'eau.

**Du squelette au code :** le filtrage est `[s for s in scores if s is not None]` dans `barriere`, suivi du refus explicite ; la boucle de comptage est `sum(1 for s in mesures if s == 1.0)` ; l'intervalle est `wilson(fideles, len(mesures))` ; la comparaison finale est `ok = bas >= seuil`. Les agrégats `macro` et `micro` se calculent sur la même liste et vont dans le rapport, mais ce n'est pas eux que la barrière compare au seuil.

## Cas d'usage réels aux Émirats

Les seuils, volumes et scores ci-dessous sont illustratifs ; les règles citées sont à confirmer avec le texte en vigueur. Dans tous ces domaines à fort enjeu, un score bas bloque la réponse automatique.

### Banque — un rapport de conformité sans affirmation inventée

Une banque de détail de Dubaï fait rédiger par un agent la première version des rapports de conformité et des recommandations d'investissement destinés à ses clients patrimoniaux, à partir des circulaires internes et des documents réglementaires récupérés. Une affirmation inventée dans ce type de document, par exemple un plafond ou une exigence que la CBUAE n'a jamais posé, engage la banque devant son régulateur. L'équipe exige un seuil strict de 0,95, appliqué à la borne basse de Wilson du taux de rapports entièrement fidèles, et la démonstration en tire une conséquence immédiate : il faut au moins 73 rapports de test, tous fidèles, pour certifier ce seuil, et un jeu de 50 ne le pourra jamais. Chaque affirmation rejetée par le juge est journalisée avec le passage du contexte qui la contredit, et un analyste conformité relit ces rejets avant chaque mise en production. Sans cette mesure, un modèle qui « complète » les règles avec ce qu'il a appris ailleurs passerait inaperçu jusqu'à un contrôle. On suit la borne basse de Wilson par version et le nombre d'affirmations rejetées par rapport.

### Immobilier — une description de bien qui n'invente pas de caractéristique

Une agence de Dubaï et d'Abu Dhabi génère les descriptions de ses annonces à partir de la fiche du bien : surface en sqft, nombre de chambres, charges de copropriété annuelles, statut off-plan et date de livraison prévue, enregistrement Ejari pour les locations. Un modèle de langage ajoute volontiers « vue sur la mer » ou « parking inclus » parce que ces mots accompagnent souvent les annonces du quartier. Chaque description est découpée en affirmations, et toute affirmation absente de la fiche est rejetée ; une seule affirmation rejetée renvoie l'annonce en relecture. Sur une annonce off-plan, une date de livraison inventée est particulièrement grave : elle peut fonder la décision d'achat et finir en litige. Sans ce contrôle, l'agence publierait des caractéristiques que le bien n'a pas, et la confiance des acheteurs en pâtirait. On suit le taux d'annonces renvoyées en relecture et le motif des rejets, par type d'affirmation.

### Crypto — une analyse de protocole fidèle au livre blanc

Une plateforme d'actifs virtuels agréée par la VARA publie pour ses clients des fiches d'analyse des jetons qu'elle liste, rédigées par un agent à partir du livre blanc et de la documentation technique de chaque projet. L'agent ne doit inventer aucun mécanisme de tokenomics : calendrier de déblocage, mécanisme de rachat et de destruction, rendement de mise en jeu. Une telle invention rend la communication trompeuse, ce que la plateforme doit éviter au regard des exigences de la VARA sur la communication à ses clients. Chaque fiche est soumise au juge affirmation par affirmation, et toute affirmation chiffrée (pourcentage, date, volume) absente du livre blanc bloque la publication. Sans cette mesure, l'agent comblerait les silences du livre blanc avec les mécanismes d'autres projets qu'il a vus à l'entraînement. On suit la Faithfulness par fiche et la part d'affirmations chiffrées rejetées.

### Crédit — la justification d'une décision, et rien d'autre

L'agent crédit d'une banque de détail explique à un client pourquoi sa demande de prêt personnel est refusée. Les règles récupérées disent que le ratio d'endettement total, toutes mensualités comprises, ne doit pas dépasser 50 % du revenu régulier. Le dossier du client indique un salaire de 25 000 AED, des mensualités existantes de 8 000 AED et une nouvelle mensualité de 5 500 AED, soit un ratio de 13 500 / 25 000 = 54 %. L'affirmation « votre ratio d'endettement atteindrait 54 %, au-dessus du plafond de 50 % » est justifiée ; l'affirmation « le plafond est de 40 % pour les salariés du privé » est inventée, et la réponse est bloquée. Une justification infidèle est à la fois une erreur envers le client et un risque de réclamation que la banque ne pourra pas défendre. On suit la Faithfulness des justifications de refus et le taux de réclamations sur les décisions de crédit.

### Assurance — montants, délais et exclusions

Un assureur auto et santé laisse un agent répondre aux questions des assurés sur leurs garanties, à partir des conditions générales et particulières de leur contrat. C'est exactement l'exemple de la démonstration : un plafond de 5 000 AED justifié, une franchise de 1 000 AED inventée, une exclusion dont la condition a disparu, soit un score de 1/3. L'assureur compare automatiquement les montants de chaque réponse aux montants du contexte, ce qui attrape la franchise inventée avant même le juge, puis fait juger les autres affirmations par un LLM. Une réponse fausse sur une franchise ou un délai de déclaration de sinistre crée une attente que l'assureur ne tiendra pas, et finit en réclamation. On suit la Faithfulness par type de question (franchise, plafond, délai, exclusion), parce qu'une moyenne globale cachait que les exclusions étaient le point faible.

### RH — l'indemnité de fin de service, au jour près

Un cabinet RH multi-émirats répond aux salariés de ses clients du secteur privé sur leur indemnité de fin de service. Les règles récupérées, tirées du décret-loi fédéral 33/2021, disent : au moins un an de service, 21 jours de salaire de base par an pour les cinq premières années, 30 jours au-delà, au prorata, avec un plafond de 24 mois de salaire de base ; les ressortissants émiriens et les employés du DIFC relèvent d'autres régimes. Pour un salaire de base de 10 000 AED et 7 ans de service, la réponse fidèle est 55 000 AED. Une réponse qui annonce « 30 jours par an dès la première année », soit 70 000 AED, contient une affirmation inventée, et le juge la rejette. Ces chiffres engagent l'employeur client et peuvent finir devant le MOHRE : le cabinet bloque toute réponse dont une affirmation chiffrée est rejetée. On suit la Faithfulness des réponses chiffrées et l'écart, en AED, entre les montants annoncés et les montants recalculés par l'outil de calcul.

## Pièges et limites

- **Prendre la fidélité pour la vérité.** Un document faux, fidèlement recopié, donne un score de 1 : la Faithfulness juge la génération, pas la base documentaire.
- **Renvoyer NaN pour une réponse sans affirmation.** Toutes les comparaisons avec NaN sont fausses, et une barrière « bloquer si score < seuil » le laisse passer ; on renvoie `None`, on compte ces réponses à part, et une barrière sans mesure refuse.
- **Mélanger macro et micro.** Ils diffèrent dès que les réponses n'ont pas le même nombre d'affirmations (0,667 contre 0,4 dans l'exemple) ; on en choisit un et on l'écrit.
- **Comparer le score brut au seuil.** On compare la borne basse de Wilson, sur les réponses et non sur les affirmations, et l'on dimensionne le jeu : 73 réponses au minimum pour un seuil de 0,95.
- **Se fier au découpage en affirmations.** L'extraction est faite par un LLM : une affirmation composée (« le plafond est de 5 000 AED et aucune franchise ne s'applique ») jugée d'un bloc masque une erreur. Le score dépend aussi du juge, qui n'est pas déterministe (étape 53).

### Exercice feuille blanche

1. Sans regarder le code, écrire `faithfulness` et `micro`, puis calculer à la main macro et micro pour trois réponses de scores 2/2, 1/4 et 0/2. (Réponse : macro (1 + 0,25 + 0)/3 = 0,417 ; micro 3/8 = 0,375.)
2. Prédire, puis vérifier avec `n_minimum` : combien de réponses toutes fidèles faut-il pour certifier un seuil de 0,98 ? (Réponse : 0,98 × 3,8416 / 0,02 = 188,2, soit 189.)
3. Trouver le bug : une barrière s'écrit `if statistics.mean(scores) < seuil: sys.exit(1)` sur une liste qui contient `float('nan')` pour les réponses sans affirmation. Que se passe-t-il ? (Réponse : la moyenne vaut NaN, la comparaison est fausse, la barrière ne bloque jamais.)

## Pour aller plus loin

- Une fidélité approchée sans LLM, par correspondance des nombres et des entités entre la réponse et le contexte, sert de garde-fou rapide en ligne ; elle est utilisée à l'étape 29.
- Les juges graduent parfois chaque affirmation (justifiée, partiellement, contredite) au lieu d'un oui ou non ; le score devient alors une moyenne pondérée, et ses propriétés de bornes restent vraies.
- Les preuves de monotonie et le lien avec la précision de l'étape 50 sont repris à l'étape 64 bis.

> Suite : [Answer Relevancy](<55-Evaluation-Formule-Answer-Relevancy.md>) — étape 55.
