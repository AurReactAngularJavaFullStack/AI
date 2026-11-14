# Palier 10 — Évaluation : mesurer l'agent, et savoir dire non

> Palier 10 sur 12 · Précédent : [Palier 09 — Garde-fous](<../09-Garde-Fous/README.md>) · Suivant : [Palier 11 — Production et coûts](<../11-Production-et-Couts/README.md>) · Leçons à relire : [Étape 13 bis — Évaluation, définitions](<../../03-Schemas-Outils-et-Premiere-Evaluation/13b-Evaluation-Definitions-Fondamentaux.md>) · [Étape 50 — Précision, rappel, F1](<../../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>) · [Étape 54 — Fidélité](<../../10-Evaluation/54-Evaluation-Formule-Faithfulness.md>) · [Étape 59 — Tool Call F1](<../../10-Evaluation/59-Evaluation-Formule-Tool-Call-F1.md>) · [Étape 60 — Goal Accuracy](<../../10-Evaluation/60-Evaluation-Formule-Agent-Goal-Accuracy.md>) · [Étape 60 bis — Petits échantillons](<../../10-Evaluation/60b-Loi-Beta-et-Petits-Echantillons.md>) · [Étape 65 — Cas d'usage et barrière](<../../10-Evaluation/65-Evaluation-Exemples-Cas-Usage.md>) · [Étape 77 — Projet final, section 9](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Démonstrations : [12 — Précision](<../../Demonstrations/04-Recherche/12_precision.md>) · [13 — Rappel](<../../Demonstrations/04-Recherche/13_rappel.md>) · [14 — Score F1](<../../Demonstrations/04-Recherche/14_score_f1.md>) · [26 — NDCG](<../../Demonstrations/04-Recherche/26_ndcg.md>) · [33 — MRR](<../../Demonstrations/04-Recherche/33_mrr.md>)

L'équipe a modifié le prompt de l'agent de crédit. Sur les premiers dossiers essayés à la main, la nouvelle version, la « candidate », répond plus vite et paraît aussi juste. Faut-il la déployer ? Ce palier répond par un programme, pas par une impression : il fait tourner les deux versions sur un jeu de dossiers de référence, mesure pour chaque dossier les outils appelés, le résultat obtenu et les chiffres inventés, agrège ces mesures avec leur incertitude, et rend un **code de sortie** : 0, la version peut partir ; 1, elle est bloquée, avec les motifs.

C'est la section 9 de l'étape 77, avec les mêmes formules et les mêmes nombres : la production réussit 18 cas sur 18 et passe (code 0) ; la candidate en réussit 14 sur 18, sa Tool Call F1 tombe à 0,926 et sa fidélité à 0,889, et la barrière la bloque (code 1). Les tests reprennent ces nombres. La démo de ce palier utilise un autre jeu de 18 dossiers, où la candidate n'en réussit que 13 ; la section « Pourquoi la démo donne 13 sur 18 » de la spécification explique l'écart.

## Où en est l'agent

Les paliers 01 à 09 ont construit un agent complet : prompt, schémas, outils métier, registre, boucle, mémoire, recherche, plan et garde-fous. Il manque la capacité de **se mesurer**. Sans mesure, chaque changement de prompt, de modèle ou d'outil est un pari.

Ce palier ajoute `agent/evaluation.py`. Ce module ne s'exécute pas **dans** la boucle : il tourne **autour** d'elle, hors ligne, sur un jeu de cas dont on connaît la bonne réponse.

```text
  jeu de référence : dossiers C-1 … C-18, avec pour chacun les appels attendus et le verdict attendu
        │ pour chaque cas
        ▼
  executer_agent (05), outils du registre (04) ─► res = {statut, reponse, trace}
        │
        ▼
  ╔═ agent/evaluation.py ═══ PALIER 10 ═════════════════════════════════════╗
  ║ noter(res, sources, attendus, but)                                      ║
  ║    tool_call_f1(attendus, appels de la trace)    le chemin              ║
  ║    but, critère métier calculé par l'appelant    le résultat            ║
  ║    fidelite_approchee(reponse, sources)          les chiffres inventés  ║
  ║ rapport(notes)  n, succès, goal_accuracy, wilson, moyennes définies     ║
  ║ barriere_ci(rapport, SEUILS)  (0, []) déployer  ou  (1, motifs) bloquer ║
  ╚═════════════════════════════════════════════════════════════════════════╝
        │
        ▼
  le script d'intégration continue appelle sys.exit(code), hors du module
```

Dans la boucle percevoir → décider → agir → observer, l'évaluation est une **observation** élargie : au lieu de lire le résultat d'un outil pour décider de l'étape suivante, on lit la trace entière d'une exécution pour juger l'agent. La Tool Call F1 juge le couple décider → agir (a-t-il appelé les bons outils, avec les bons arguments ?), la Goal Accuracy juge le résultat (le dossier a-t-il le bon verdict ?), la fidélité juge la réponse (cite-t-elle des chiffres qui ne viennent d'aucune source ?). Les mesures de ce palier alimentent aussi les garde-fous : l'incertitude u du palier 09 peut valoir 1 − fidélité.

## Ce que tu vas coder

- `wilson(succes, n, z)` : l'intervalle de Wilson à 95 % d'une proportion ; `None` si n = 0.
- `tool_call_f1(attendus, reels)` : la F1 des appels d'outils, sur des multi-ensembles ; `None` si rien n'était attendu ni fait.
- `goal_accuracy(resultats)` : la part des tâches réussies ; `None` sans tâche.
- `nombres(t)` : les nombres cités dans un texte, lus à la française, pourcentages divisés par 100.
- `fidelite_approchee(reponse, sources)` : la part des nombres de la réponse que l'on retrouve dans les sources ; `None` si la réponse n'en cite aucun.
- `moyenne_definie(valeurs)` : la moyenne des valeurs qui ne sont pas `None`.
- `noter(res, sources, attendus, but)` : les trois mesures d'un cas.
- `rapport(notes)` : l'agrégat d'un jeu de cas.
- `barriere_ci(rap, seuils)` : le code de sortie 0 ou 1 et ses motifs ; la constante `SEUILS` est fournie.

## Rappel de cours

Le taux de réussite mesuré sur n tâches, dont s réussies :

$$
\widehat{GA} = \frac{1}{n} \sum_{i=1}^{n} y_i = \frac{s}{n}
$$

Son intervalle de Wilson à 95 % :

$$
\text{Wilson}(s, n) = \frac{\hat p + \dfrac{z^2}{2n} \pm z\sqrt{\dfrac{\hat p\,(1-\hat p)}{n} + \dfrac{z^2}{4n^2}}}{1 + \dfrac{z^2}{n}}
\qquad \hat p = \frac{s}{n}
$$

La Tool Call F1, sur des multi-ensembles de clés d'appel :

$$
TP = \sum_{c} \min\big(n_{att}(c),\ n_{réel}(c)\big)
\qquad
\text{Tool Call } F_1 = \frac{2\,TP}{\lvert C_{att} \rvert + \lvert C_{réel} \rvert}
$$

La fidélité approchée, sur les nombres cités :

$$
F = \frac{\big\lvert \{\, x \in X \;:\; \exists\, k \in K,\ x \approx k \,\}\big\rvert}{\lvert X \rvert}
\qquad \text{indéfinie si } X = \varnothing
$$

La moyenne des seules valeurs définies :

$$
\bar m = \frac{1}{\lvert D \rvert} \sum_{v \in D} v
\qquad \text{indéfinie si } D = \varnothing
$$

La barrière d'intégration continue, pour un jeu non vide :

$$
\text{code} = 0 \iff \text{bas} \ge \tau_{bas} \;\wedge\; \big(\bar F_1 \text{ indéfinie} \vee \bar F_1 \ge \tau_{F_1}\big) \;\wedge\; \big(\bar F \text{ indéfinie} \vee \bar F \ge \tau_{fid}\big)
$$

### Les symboles, un par un

$$
n
$$

Le nombre de cas évalués, `len(notes)` dans `rapport`.

$$
s
$$

Le nombre de cas dont l'objectif est atteint, `rapport["succes"]`.

$$
y_i
$$

La note de la tâche i : 1 si l'objectif est atteint, 0 sinon ; en Python, le booléen `but`, que `sum` compte comme 1 ou 0.

$$
\widehat{GA}
$$

La Goal Accuracy mesurée, rendue par `goal_accuracy`.

$$
\hat p
$$

La proportion observée s / n, la variable `p` de `wilson`.

$$
z
$$

Le quantile de la loi normale pour un niveau de confiance de 95 %, 1,96 ; donc z² = 3,8416.

$$
c
$$

La clé canonique d'un appel d'outil : le nom de l'outil et ses arguments écrits en JSON à clés triées.

$$
n_{att}(c)
$$

Le nombre de fois où la clé c figure dans les appels attendus.

$$
n_{réel}(c)
$$

Le nombre de fois où la clé c figure dans les appels réellement faits, lus dans la trace.

$$
TP
$$

Les vrais positifs : les appels présents des deux côtés, chaque répétition comptée au plus autant de fois qu'elle était attendue.

$$
C_{att}
$$

Le multi-ensemble des appels attendus ; sa taille compte les répétitions.

$$
C_{réel}
$$

Le multi-ensemble des appels faits.

$$
X
$$

La liste des nombres cités par la réponse, rendue par `nombres(reponse)`.

$$
K
$$

La liste des nombres connus : tous ceux des sources (sorties d'outils, prompt, documents).

$$
x \approx k
$$

L'égalité à la tolérance de `math.isclose`, relative et absolue de 10⁻⁹ : les flottants issus d'un calcul et d'un texte ne sont pas toujours égaux au dernier bit.

$$
F
$$

La fidélité approchée d'une réponse, dans [0, 1] ; 1 veut dire qu'aucun nombre n'est inventé.

$$
D
$$

Les valeurs définies d'une liste de mesures, c'est-à-dire celles qui ne valent pas `None`.

$$
\bar F_1
$$

La moyenne définie des Tool Call F1 des cas, `rapport["tool_f1"]`.

$$
\bar F
$$

La moyenne définie des fidélités des cas, `rapport["fidelite"]`.

$$
\text{bas}
$$

La borne basse de l'intervalle de Wilson du taux de réussite, `rapport["wilson"][0]`.

$$
\tau_{bas}
$$

Le seuil de la borne basse, 0,80 (`SEUILS["borne_basse"]`, illustratif).

$$
\tau_{F_1}
$$

Le seuil de la Tool Call F1 moyenne, 0,95 (`SEUILS["tool_f1"]`, illustratif).

$$
\tau_{fid}
$$

Le seuil de la fidélité moyenne, 0,95 (`SEUILS["fidelite"]`, illustratif).

### Pourquoi dix-huit cas réussis, et pas trois

Quand tous les cas réussissent, p̂ = 1 et le terme p̂(1 − p̂) s'annule. La demi-largeur vaut alors (z²/2n) / (1 + z²/n) et le centre (1 + z²/2n) / (1 + z²/n), d'où une forme simple de la borne basse :

$$
\text{bas}(n \text{ sur } n) = \frac{1 + \frac{z^2}{2n} - \frac{z^2}{2n}}{1 + \frac{z^2}{n}} = \frac{n}{n + z^2}
$$

Trois cas parfaits ne prouvent qu'un taux de 0,438, et la barrière les refuse. Pour prouver 80 %, il faut :

$$
\frac{n}{n + z^2} \ge 0{,}8 \iff 0{,}2\, n \ge 0{,}8\, z^2 \iff n \ge 4 z^2 = 15{,}37
$$

soit au moins 16 cas parfaits. Le jeu de référence en compte 18, qui donnent 18 / 21,8416 = 0,824 : la production passe.

### Pourquoi la F1 s'écrit avec les tailles des deux listes

Chaque appel attendu est soit trouvé (TP), soit oublié (FN) ; chaque appel fait est soit attendu (TP), soit en trop (FP). Donc |C_att| = TP + FN et |C_réel| = TP + FP, et la F1 de l'étape 50 se réécrit :

$$
F_1 = \frac{2\,TP}{2\,TP + FP + FN} = \frac{2\,TP}{\lvert C_{att} \rvert + \lvert C_{réel} \rvert}
$$

C'est la forme qu'on code : il suffit de compter TP et les deux tailles. Si les deux listes sont vides, le dénominateur est nul : la F1 est indéfinie, pas égale à 1 (une abstention correcte se mesure à part) ni à 0.

### Pourquoi None, et pas 0

Une métrique sans dénominateur n'a pas de valeur. Lui donner 0 punirait un cas qui ne pouvait pas être mesuré (une réponse sans aucun chiffre n'a rien inventé) ; lui donner 1 le récompenserait. La convention du parcours : la fonction rend `None`, et la moyenne l'ignore. Dix-huit cas dont la fidélité vaut `None` ne bloquent donc pas la barrière sur la fidélité : il n'y a rien à juger.

## Spécification

### `wilson`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`wilson(succes, n, z)`** — Cette fonction doit parler comme un sondeur prudent qui refuse d'annoncer un chiffre sec et donne toujours une fourchette, d'autant plus large qu'il a interrogé peu de monde. Elle reçoit le nombre de succès, le nombre de cas et le quantile z, 1,96 par défaut pour 95 % ; elle doit rendre `None` si n vaut 0, avant tout autre test, lever `ValueError("il faut 0 <= succes <= n")` si n est négatif ou si les succès sortent de [0, n], et sinon rendre le couple (borne basse, borne haute) de l'intervalle de Wilson. Pour 14 sur 18, la fourchette attendue est [0,548 ; 0,910], pour 18 sur 18 la borne basse vaut 0,824, et pour 3 sur 3 elle tombe à 0,438 : c'est cette borne basse que la barrière jugera.

```python
# [extrait] spécification
def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None: ...
```

Rend `None` si n = 0 (testé **avant** toute autre chose), lève `ValueError("il faut 0 <= succes <= n")` si n < 0 ou si `succes` sort de [0, n], et sinon le couple (borne basse, borne haute) de la formule ci-dessus.

Exemple déroulé (tests `TestWilson`). Pour 14 sur 18, p̂ = 0,7778, z²/n = 0,2134, donc le dénominateur vaut 1,2134 et le centre (0,7778 + 0,1067) / 1,2134 = 0,7289. Sous la racine, 0,7778 × 0,2222 / 18 + 3,8416 / 1 296 = 0,009602 + 0,002964 = 0,012566, dont la racine vaut 0,11210 ; la demi-largeur vaut 1,96 × 0,11210 / 1,2134 = 0,1811. L'intervalle est donc :

$$
[\,0{,}7289 - 0{,}1811 \;;\; 0{,}7289 + 0{,}1811\,] = [\,0{,}548 \;;\; 0{,}910\,]
$$

Pour 18 sur 18, la borne basse vaut 18 / 21,8416 = 0,824 et la haute 1. Pour 3 sur 3, 3 / 6,8416 = 0,438. `wilson(0, 0)` vaut `None`, et `wilson(5, 4)` lève `ValueError`.

### `tool_call_f1`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tool_call_f1(attendus, reels)`** — On attend de cette fonction le travail d'un inspecteur de chantier qui compare la liste des interventions prévues à celle des interventions réellement faites, en comptant les doublons comme des fautes. Elle reçoit deux listes de couples `(nom, arguments)`, transforme chaque appel en clé canonique formée du nom et des arguments écrits en JSON à clés triées, compte ces clés de chaque côté, prend l'intersection des comptes pour obtenir TP, et rend 2 × TP / (|A| + |R|). Elle doit rendre `None` si les deux listes sont vides : deux appels attendus et faits donnent 1, un seul des deux donne 2/3, un appel attendu une fois mais fait deux fois donne aussi 2/3, et un appel attendu jamais fait donne 0,0.

```python
# [extrait] spécification
def tool_call_f1(attendus: list, reels: list) -> float | None: ...
```

`attendus` et `reels` sont des listes de couples `(nom, arguments)`, où `arguments` est un dictionnaire. Chaque appel devient une clé canonique `(nom, json.dumps(arguments, sort_keys=True))` : un dictionnaire n'est pas hachable, et deux appels qui ne diffèrent que par l'ordre de leurs arguments doivent donner la même clé. On compte les clés de chaque côté dans un `Counter`, on prend l'intersection `&` (le minimum des multiplicités), et l'on rend 2 × TP / (|A| + |R|), ou `None` si les deux listes sont vides.

Exemple déroulé (tests `TestToolCallF1`). Le dossier C-1 attend la mensualité (A1) puis le ratio (A2). Les deux appels faits : TP = 2 et F1 = 4 / 4 = 1. Seulement A1 : TP = 1, F1 = 2 × 1 / (2 + 1) = 2/3 ≈ 0,6667. A1 attendu une fois mais fait deux fois : min(1, 2) = 1, F1 = 2 / (1 + 2) = 2/3 aussi, la répétition est pénalisée comme un oubli. A1 avec ses arguments dans un autre ordre : même clé, F1 = 1. Rien attendu, rien fait : `None`. A1 attendu, rien fait : 2 × 0 / 1 = 0,0.

### `goal_accuracy`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`goal_accuracy(resultats)`** — Cette fonction doit tenir le rôle de l'arbitre qui, à la fin du tournoi, compte simplement les matchs gagnés et les divise par les matchs joués. Elle reçoit une liste de booléens, un par tâche, où `True` signifie que l'objectif métier du dossier a été atteint, et doit rendre leur moyenne, `True` comptant pour 1 et `False` pour 0. Pour une liste vide, elle rend `None` plutôt qu'une division par zéro ; avec 14 vrais et 4 faux, elle rend 14 / 18 ≈ 0,7778, le taux de réussite que le rapport affichera à côté de son intervalle de Wilson.

```python
# [extrait] spécification
def goal_accuracy(resultats: list[bool]) -> float | None: ...
```

La moyenne des booléens (`True` compte 1), ou `None` pour une liste vide. Exemple (test `test_goal_accuracy`) : 14 vrais et 4 faux donnent 14 / 18 ≈ 0,7778.

### `nombres`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`nombres(t)`** — Cette fonction doit lire un texte comme un correcteur qui surligne au feutre jaune chaque chiffre cité, après avoir rayé les renvois de bas de page. Elle reçoit une chaîne, doit d'abord retirer les citations de la forme `[REG-1]`, puis les espaces fines U+202F qui séparent les milliers, et enfin lire chaque nombre écrit avec une virgule ou un point décimal, en divisant par 100 ceux que suit un `%`. Elle rend la liste de ces nombres en flottants : « 5 558,32 AED ; 28,9 % [REG-1] » doit donner `[5558.32, 0.289]`, et « aucun chiffre [REG-2] » une liste vide, puisque le 2 de la citation ne compte pas.

```python
# [extrait] spécification
def nombres(t: str) -> list[float]: ...
```

Retire d'abord les citations de la forme `[REG-1]` (lettres majuscules, tiret, chiffres), qui ne sont pas des chiffres cités, puis les espaces fines (`ESPACE_FINE`, U+202F, le séparateur de milliers que `fr` du palier 03 produit). Lit ensuite chaque nombre, avec une virgule ou un point décimal, éventuellement suivi d'espaces et d'un `%` : un pourcentage est divisé par 100.

Exemple déroulé (test `test_nombres_a_la_francaise`) : « 5 558,32 AED ; 28,9 % [REG-1] », écrit avec une espace fine, perd sa citation et son espace fine et devient « 5558,32 AED ; 28,9 % » ; on lit 5558,32, puis 28,9 suivi de « % », soit 0,289. Résultat `[5558.32, 0.289]`. « aucun chiffre [REG-2] » donne une liste vide : le 2 de la citation ne compte pas.

### `fidelite_approchee`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fidelite_approchee(reponse, sources)`** — Cette fonction doit se conduire comme un vérificateur de faits dans une rédaction, qui reprend chaque chiffre de l'article et cherche dans les dépêches s'il y figure. Elle reçoit la réponse de l'agent et la liste des sources, extrait avec `nombres` les nombres X de la réponse et rend `None` s'il n'y en a aucun ; sinon elle réunit les nombres K de toutes les sources et rend la part des éléments de X qui ont un voisin dans K au sens de `math.isclose` avec des tolérances de 10⁻⁹. La réponse de la candidate qui cite 5419,37 et 35 % face à une seule sortie d'outil donnant 5419,37 obtient 1 / 2 = 0,5 ; avec une source « plafond 35 % » en plus, elle obtient 1.

```python
# [extrait] spécification
def fidelite_approchee(reponse: str, sources: list[str]) -> float | None: ...
```

X = `nombres(reponse)`. Si X est vide, `None`. Sinon K réunit les nombres de toutes les sources, et la fonction rend la part des éléments de X qui ont un élément de K proche au sens de `math.isclose(x, k, rel_tol=1e-9, abs_tol=1e-9)`.

Exemple déroulé (test `test_fidelite`). La réponse de la candidate, « Mensualité 5 419,37 AED ; endettement estimé à 35 % : dossier recevable. », cite X = [5419,37 ; 0,35]. La seule source, la sortie de l'outil `{"mensualite_aed": 5419.37}`, donne K = [5419,37]. Le premier nombre est retrouvé, pas le second : F = 1 / 2 = 0,5. Si l'on ajoute une source « plafond 35 % », 0,35 devient connu et F = 1. « Dossier recevable. » ne cite aucun nombre : `None`.

### `moyenne_definie`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`moyenne_definie(valeurs)`** — Cette fonction doit ressembler au professeur qui calcule la moyenne de la classe en laissant de côté les copies blanches des absents, plutôt que de leur mettre zéro. Elle reçoit une liste de mesures dont certaines valent `None`, ne garde que les valeurs définies et rend leur moyenne arithmétique ; s'il n'en reste aucune, elle rend `None`. Ainsi [1 ; None ; 0,5] doit donner (1 + 0,5) / 2 = 0,75 et [None ; None] doit donner `None` : c'est elle qui permet au rapport de moyenner les F1 et les fidélités sans punir les cas qui n'étaient pas mesurables.

```python
# [extrait] spécification
def moyenne_definie(valeurs: list) -> float | None: ...
```

La moyenne des valeurs qui ne sont pas `None` ; `None` s'il n'y en a aucune. Exemple (test `test_moyenne_definie`) : [1 ; None ; 0,5] donne (1 + 0,5) / 2 = 0,75 ; [None ; None] donne `None`.

### `noter`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`noter(res, sources, attendus, but)`** — Cette fonction doit jouer l'examinateur qui remplit, pour une seule copie, la fiche à trois cases : le chemin suivi, le résultat obtenu, la fidélité des chiffres. Elle reçoit le dictionnaire `res` rendu par `executer_agent`, les sources du cas, les appels attendus et le booléen `but` calculé par l'appelant ; elle extrait les couples `(nom, arguments)` des lignes de `res["trace"]`, calcule leur Tool Call F1, et calcule la fidélité de `res["reponse"]` seulement si le statut vaut `"fini"`, sinon elle met `None`. Elle rend le dictionnaire aux clés `"f1"`, `"but"` et `"fidelite"` : 2/3, vrai et 1 pour une exécution finie qui n'a appelé que A1, 0,0 et `None` pour une exécution tronquée sans trace.

```python
# [extrait] spécification
def noter(res: dict, sources: list[str], attendus: list, but: bool) -> dict: ...
```

`res` est le dictionnaire rendu par `executer_agent` (palier 05). Les appels réels sont les couples `(nom, arguments)` des lignes `(nom, arguments, sortie)` de `res["trace"]`. La fonction rend `{"f1": tool_call_f1(attendus, reels), "but": but, "fidelite": …}`, où la fidélité vaut `fidelite_approchee(res["reponse"], sources)` si `res["statut"] == "fini"`, et `None` sinon : un résultat tronqué ou en boucle n'a pas de clé `"reponse"`. Le critère `but` est calculé par l'appelant, qui seul connaît l'objectif métier du cas.

Exemple déroulé (test `test_noter`). Une exécution finie qui n'a appelé que A1, dont la réponse « Mensualité 5419,37 AED. » cite un nombre présent dans la sortie de l'outil, avec A1 et A2 attendus : F1 = 2/3, fidélité = 1, but vrai. Une exécution tronquée, sans trace, avec A1 attendu : F1 = 0,0 et fidélité `None`.

### `rapport`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`rapport(notes)`** — Cette fonction doit être le secrétaire du jury qui rassemble toutes les fiches individuelles et en tire le bulletin de la promotion. Elle reçoit la liste des notes produites par `noter` et rend un dictionnaire aux six clés `"n"`, `"succes"`, `"taux"`, `"wilson"`, `"tool_f1"` et `"fidelite"` : le nombre de notes, le nombre de buts atteints, la Goal Accuracy de ces buts, l'intervalle de Wilson correspondant, et les moyennes définies des F1 et des fidélités. Pour 14 cas parfaits et 4 cas fautifs à F1 2/3 et fidélité 0,5, elle doit donner n = 18, 14 succès, une F1 moyenne de 0,926 et une fidélité moyenne de 0,889.

```python
# [extrait] spécification
def rapport(notes: list[dict]) -> dict: ...
```

Rend `{"n", "succes", "taux", "wilson", "tool_f1", "fidelite"}` : le nombre de notes, le nombre de buts atteints, `goal_accuracy` des buts, `wilson(succes, n)`, et les moyennes **définies** des F1 et des fidélités.

Exemple déroulé (test `test_candidate_bloquee_avec_trois_motifs`). 14 cas parfaits (F1 1, fidélité 1, but vrai) et 4 cas fautifs (F1 2/3, fidélité 0,5, but faux) : n = 18, succes = 14, et

$$
\bar F_1 = \frac{14 \times 1 + 4 \times \frac{2}{3}}{18} = \frac{16{,}667}{18} = 0{,}926
\qquad
\bar F = \frac{14 \times 1 + 4 \times 0{,}5}{18} = \frac{16}{18} = 0{,}889
$$

### `barriere_ci`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`barriere_ci(rap, seuils)`** — Cette fonction doit tenir le poste du contrôleur technique qui, à la sortie de l'usine, relit le bulletin et appose ou non le tampon « bon pour la route ». Elle reçoit le rapport et le dictionnaire de seuils, `SEUILS` par défaut ; si le rapport compte zéro cas, elle rend `(1, ["aucun cas évalué"])`, sinon elle compare la borne basse de Wilson à 0,8, la F1 moyenne à 0,95 et la fidélité moyenne à 0,95, en ajoutant un motif à trois décimales pour chaque seuil violé et en ignorant une moyenne `None`. Elle rend `(0, [])` si aucun motif n'est apparu, `(1, motifs)` sinon, sans jamais appeler `sys.exit` : la candidate à 14 sur 18 récolte trois motifs, la production à 18 sur 18 passe avec 0,824.

```python
# [extrait] spécification
SEUILS = {"borne_basse": 0.80, "tool_f1": 0.95, "fidelite": 0.95}


def barriere_ci(rap: dict, seuils: dict = SEUILS) -> tuple[int, list[str]]: ...
```

Si `rap["n"] == 0`, rend `(1, ["aucun cas évalué"])` : un jeu vide ne prouve rien, et `rap["wilson"]` vaut alors `None`. Sinon, un motif par seuil violé, dans cet ordre et avec les valeurs à trois décimales : `"borne basse de Wilson 0.548 < 0.8"`, `"Tool Call F1 0.926 < 0.95"`, `"fidélité approchée 0.889 < 0.95"`. Une moyenne `None` ne crée pas de motif. Le code vaut 1 s'il y a au moins un motif, 0 sinon. La fonction n'appelle **jamais** `sys.exit` : c'est le script de CI qui le fait avec le code rendu.

Exemple déroulé. La candidate (14 sur 18) viole les trois seuils : 0,548 < 0,80, 0,926 < 0,95 et 0,889 < 0,95, donc `(1, [trois motifs])`. La production (18 sur 18, F1 et fidélité à 1) : 0,824 ≥ 0,80, `(0, [])`. Trois cas parfaits seulement : 0,438 < 0,80, `(1, ["borne basse de Wilson 0.438 < 0.8"])` (test `test_production_passe_trois_cas_ne_suffisent_pas`). Dix-huit cas réussis dont F1 et fidélité valent `None` : `(0, [])` (test `test_moyenne_indefinie_ne_bloque_pas`).

### Pourquoi la démo donne 13 sur 18, et le palier 12 14 sur 18

La démo de ce palier évalue les **18 variantes** C-1 à C-18 du dossier de crédit : principal 1 000 000 − 25 000 i AED, revenu 40 000 − 1 500 i AED, mensualités en cours 6 000 + 500 i AED. La candidate saute le calcul du ratio et invente « endettement estimé à 35 % » quand i est de la forme 4k + 1, c'est-à-dire pour i = 1, 5, 9, 13 et **17** : cinq cas fautifs, donc 13 sur 18, une Tool Call F1 de (13 + 5 × 2/3) / 18 = 0,907, une fidélité de (13 + 5 × 0,5) / 18 = 0,861, et un intervalle de Wilson [0,491 ; 0,875].

L'étape 77 et le palier 12 utilisent un autre jeu de 18 cas : les **trois scénarios** de bout en bout (hypothèque, question réglementaire, virement piégé), réussis par les deux versions, plus les **15 variantes** i = 1 à 15, parmi lesquelles le défaut ne touche que i = 1, 5, 9 et 13. Quatre cas fautifs : 14 sur 18, 0,926 et 0,889. Même défaut, mêmes formules, autre jeu de référence : un taux ne se compare qu'à un taux mesuré sur **les mêmes cas**. Les tests de ce palier reprennent les nombres de 77 avec des notes construites à la main (14 parfaites, 4 fautives).

### Ce qui change par rapport à l'étape 77

Les fonctions sont celles de la section 9 de l'étape 77 (et `wilson` celle de la section 4), recopiées sans changement de logique. Deux ajouts seulement : `barriere_ci` reçoit `SEUILS` comme valeur par défaut de `seuils`, et `wilson` refuse aussi un n négatif.

## Squelette algorithmique

```text
ALGORITHME Wilson(s, n, z)
  SI n = 0 ALORS RETOURNER rien
  SI n < 0 OU s < 0 OU s > n ALORS ERREUR
  p ← s / n ; d ← 1 + z² / n
  centre ← (p + z² / 2n) / d
  demi ← z × racine(p (1 − p) / n + z² / 4n²) / d
  RETOURNER (centre − demi, centre + demi)

ALGORITHME ToolCallF1(attendus, réels)
  A ← comptage des clés (nom, arguments en JSON trié) des attendus
  R ← comptage des clés des réels
  total ← taille de A + taille de R
  SI total = 0 ALORS RETOURNER rien
  TP ← somme sur les clés c de min(A[c], R[c])
  RETOURNER 2 × TP / total

ALGORITHME Fidélité(réponse, sources)
  X ← Nombres(réponse)                         (citations retirées, lecture à la française)
  SI X est vide ALORS RETOURNER rien
  K ← Nombres de chaque source, réunis
  RETOURNER (nombre de x de X proches d'un k de K) / taille de X

ALGORITHME BarrièreCI(jeu de cas, seuils)
  notes ← liste vide
  POUR CHAQUE cas DU jeu FAIRE
      résultat ← BoucleAgent(cas)
      ajouter à notes : (ToolCallF1(attendus, appels de la trace), but du cas,
                         Fidélité(réponse, sources) SI le statut est fini SINON rien)
  FIN POUR
  SI notes est vide ALORS RETOURNER (1, « aucun cas évalué »)
  succès ← nombre de buts atteints ; (bas, haut) ← Wilson(succès, taille de notes)
  F ← moyenne des F1 définies ; G ← moyenne des fidélités définies
  motifs ← liste vide
  SI bas < seuil bas ALORS ajouter « borne basse de Wilson »
  SI F est définie ET F < seuil F1 ALORS ajouter « Tool Call F1 »
  SI G est définie ET G < seuil fidélité ALORS ajouter « fidélité approchée »
  SI motifs est vide ALORS RETOURNER (0, motifs) SINON RETOURNER (1, motifs)
```

**Complexité.** Wilson coûte O(1). La Tool Call F1 d'un cas coûte O(a + r) pour a appels attendus et r appels faits : deux comptages et une intersection de dictionnaires, plus la sérialisation JSON des arguments. `nombres` est linéaire en la longueur du texte. La fidélité compare chaque nombre cité à chaque nombre connu, O(x × k) ; un ensemble ou un tri ramènerait la recherche à O(x log k), inutile pour quelques nombres. L'agrégat est en O(n) pour n cas. Le coût dominant n'est pas le calcul des métriques mais les n exécutions de la boucle : avec un vrai modèle, n × (k + 1) appels facturés pour k étapes d'outils.

**Du squelette au code.** `Wilson` est `wilson`. `ToolCallF1` est `tool_call_f1`, dont les comptages sont deux `Counter` et le minimum l'intersection `a & r`. `Nombres` est `nombres` et `Fidélité` est `fidelite_approchee`. Dans `BarrièreCI`, la ligne ajoutée à la liste est `noter`, l'agrégat (succès, Wilson, deux moyennes) est `rapport`, avec `goal_accuracy` et `moyenne_definie`, et la fin est `barriere_ci` avec les seuils `SEUILS`. La boucle sur les cas et `BoucleAgent` restent chez l'appelant : la démo et le palier 12 appellent `executer_agent` pour chaque cas.

## Cas d'usage aux Émirats

Les seuils et les volumes sont illustratifs.

### Banque — 18 dossiers de crédit avant de changer le prompt

Une banque de détail de Dubaï garde un jeu de 18 dossiers de crédit de référence, C-1 à C-18, chacun avec ses deux appels attendus (mensualité, puis ratio d'endettement CBUAE) et son verdict, « recevable » si le ratio reste sous 50 % du revenu. La version en production réussit les 18 : borne basse de Wilson 0,824, Tool Call F1 et fidélité à 1, code 0. La candidate, qui saute le ratio sur cinq dossiers et écrit « endettement estimé à 35 % », réussit 13 dossiers sur 18 : borne basse 0,491, Tool Call F1 0,907, fidélité 0,861, code 1 avec trois motifs. Chaque motif désigne un défaut : la borne basse dit que trop de dossiers échouent, la F1 qu'un outil n'a pas été appelé, la fidélité qu'un chiffre a été inventé. Sans la barrière, le dossier C-9 (ratio réel 0,5588, au-dessus du plafond) serait parti avec la mention « recevable ».

### Assurance — 45 sinistres réussis sur 50, et pourtant bloqué

Un assureur auto évalue son agent de pré-instruction des sinistres sur 50 dossiers : 45 réussis, un taux de 0,90 qui semble confortable. L'intervalle de Wilson vaut [0,786 ; 0,957] : avec si peu de cas, le vrai taux peut descendre jusqu'à 0,786, sous le seuil de 0,80, et la barrière bloque. Deux réponses possibles, et pas trois : agrandir le jeu (le même taux de 0,90 sur 100 dossiers donne une borne basse d'environ 0,826) ou corriger les cinq échecs. Baisser le seuil pour faire passer la version serait mesurer ce qu'on veut voir.

### RH — une indemnité juste, une prime inventée

Un cabinet RH fait calculer par l'agent l'indemnité de fin de service d'un salarié payé 10 000 AED de base pendant 7 ans. L'outil rend `{"indemnite_aed": 55000}` (décret-loi fédéral 33/2021 : 5 × 21 + 2 × 30 jours de salaire). La réponse de l'agent, « Indemnité 55 000,00 AED, plus une prime de 12 %. », cite deux nombres : 55 000 est dans la sortie de l'outil, 0,12 n'est nulle part. Fidélité 1 / 2 = 0,5 : l'agent a inventé une prime. Le calcul suppose que la réponse est écrite avec `fr`, donc avec l'espace fine : écrite « 55 000 » avec une espace ordinaire, elle serait lue comme les deux nombres 55 et 0, tous deux introuvables, et la fidélité tomberait à 0. Une métrique approchée a les limites de son lecteur ; on les connaît, on les teste.

## Travail à faire

1. Ouvre un terminal PowerShell dans `projet/` et lance une première fois les tests. Ceux des paliers 01 à 09 passent ; les 14 tests du palier 10 échouent tous par `NotImplementedError`.

   ```text
   cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\10-Evaluation\projet"
   & "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m unittest
   ```

   Dans la suite, `python` désigne ce chemin complet.

2. Ouvre `projet/agent/evaluation.py`. Code `wilson` (TODO 1 et 2) ; `python -m unittest -v tests.test_10_evaluation.TestWilson`.
3. Code `tool_call_f1` (TODO 3 et 4) ; `python -m unittest -v tests.test_10_evaluation.TestToolCallF1`.
4. Code `goal_accuracy`, `nombres`, `fidelite_approchee` et `moyenne_definie` (TODO 5 à 10) ; `python -m unittest -v tests.test_10_evaluation.TestGoalEtFidelite`.
5. Code `noter`, `rapport` et `barriere_ci` (TODO 11 à 14) ; `python -m unittest -v tests.test_10_evaluation.TestRapportEtBarriere`.
6. Lance toute la suite, `python -m unittest -v`, puis `python demo.py`, et compare la sortie à celle ci-dessous.

## Critères de réussite

Depuis `projet/`, `python -m unittest` affiche `Ran 136 tests` et `OK` : les 122 tests des paliers 01 à 09 et les 14 du palier 10. Puis `python demo.py` imprime exactement ceci :

### Sortie attendue de demo.py

```text
Palier 10 — 18 dossiers de crédit C-1 à C-18, version production contre version candidate
  production : 18/18   Wilson [0.824 ; 1.000]   Tool F1 1.000   fidélité 1.000   → code 0
  candidate  : 13/18   Wilson [0.491 ; 0.875]   Tool F1 0.907   fidélité 0.861   → code 1
    - borne basse de Wilson 0.491 < 0.8
    - Tool Call F1 0.907 < 0.95
    - fidélité approchée 0.861 < 0.95
Pourquoi 18 cas et pas 3 : la borne basse de n sur n vaut n / (n + 1,96²)
   3 sur 3  → borne basse 0.438
  15 sur 15 → borne basse 0.796
  16 sur 16 → borne basse 0.806
  18 sur 18 → borne basse 0.824
  aucun cas : wilson(0, 0) = None ; barrière : (1, ['aucun cas évalué'])
OK — palier 10 terminé.
```

Comment lire cette sortie. Pour chaque version, la démo fait tourner la boucle du palier 05 sur les 18 dossiers avec un faux modèle scripté, note chaque cas avec `noter`, agrège avec `rapport` et décide avec `barriere_ci`. La production passe ; la candidate est bloquée par ses trois motifs, avec 13 cas réussis pour la raison expliquée plus haut (cinq dossiers fautifs, et non quatre comme au palier 12). Le tableau suivant vérifie la formule n / (n + z²) : 15 cas parfaits donnent 0,796, juste sous 0,80, et 16 donnent 0,806, juste au-dessus, comme le prévoit le seuil de 15,37. Un jeu vide ne donne pas d'intervalle et bloque la barrière.

## Pour aller plus loin

**Défi 1 — Comparer les deux versions sur les mêmes cas.** Écris `mcnemar(b, c)`, qui rend (|b − c| − 1)² / (b + c), où b compte les cas réussis par la production et ratés par la candidate, et c l'inverse (étape 13 bis). Réponse attendue : sur la démo, b = 5 et c = 0, donc 16 / 5 = 3,2, sous la valeur critique 3,84 : la dégradation n'est pas significative à 5 % sur 18 cas, et c'est la borne basse de Wilson, pas le test, qui bloque la candidate.

**Défi 2 — Combien de cas pour un seuil de 95 % ?** Écris `cas_minimum(tau, z=1.96)`, le plus petit n tel que n / (n + z²) ≥ τ. Réponse attendue : 16 pour τ = 0,80 et 73 pour τ = 0,95, puisque 19 × 3,8416 = 72,99 ; le jeu de 18 cas ne suffit pas à prouver 95 %.

**Défi 3 — La constance, pass^k.** Fais tourner chaque cas k fois et compte un cas comme réussi seulement si ses k essais réussissent. Réponse attendue : un agent qui réussit chaque essai avec la probabilité 0,9, indépendamment, n'a plus qu'une probabilité 0,9³ = 0,729 de réussir trois fois de suite (étape 60).

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`. Ouvre seulement l'étape qui te manque :

- [Étape 1 — L'intervalle de Wilson](<solutions/progression/01-Intervalle-de-Wilson.md>) : `wilson`, la formule traduite terme à terme, et le cas n = 0.
- [Étape 2 — La Tool Call F1](<solutions/progression/02-Tool-Call-F1.md>) : clés canoniques, `Counter` et intersection de multi-ensembles.
- [Étape 3 — Goal Accuracy et moyenne définie](<solutions/progression/03-Goal-Accuracy-et-moyenne-definie.md>) : deux moyennes qui rendent `None` plutôt que 0.
- [Étape 4 — La fidélité approchée](<solutions/progression/04-Fidelite-approchee.md>) : `nombres` à la française et `fidelite_approchee`.
- [Étape 5 — Noter un cas](<solutions/progression/05-Noter-un-cas.md>) : `noter`, la trace de la boucle et le cas tronqué.
- [Étape 6 — Le rapport et la barrière CI](<solutions/progression/06-Rapport-et-barriere-CI.md>) : `rapport`, `SEUILS` et `barriere_ci`, les trois motifs.
- [Étape 7 — Assembler, tester, lancer la démo](<solutions/progression/07-Assembler-tester-lancer.md>) : la suite complète, la démo et ce qu'il faut retenir.

La solution entière est dans `solutions/agent/evaluation.py`, avec les tests dans `solutions/tests/` et la démo dans `solutions/demo.py`.
