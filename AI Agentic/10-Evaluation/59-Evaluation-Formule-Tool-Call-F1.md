# Étape 59 — Évaluation — Tool Call F1

> Étape 59 du parcours · Prérequis : [Context Recall](<58-Evaluation-Formule-Context-Recall.md>) · Suite : [Agent Goal Accuracy](<60-Evaluation-Formule-Agent-Goal-Accuracy.md>)

**Dossier :** 10-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers  
**Nom du fichier :** 59-Evaluation-Formule-Tool-Call-F1.md

## Définition

La Tool Call F1 mesure la qualité des **actions** d'un agent : elle compare les appels d'outils que l'agent a faits aux appels qu'il aurait dû faire, un appel étant le couple (nom de l'outil, arguments normalisés). Les appels présents des deux côtés sont les vrais positifs, en comptant les répétitions au plus petit des deux nombres ; les appels faits en trop sont les faux positifs ; les appels attendus mais oubliés sont les faux négatifs ; la F1 de l'étape 56 s'applique ensuite telle quelle. Comme la comparaison porte sur des **multi-ensembles**, la métrique ne dépend pas de l'ordre des appels : quand l'ordre compte (vérifier l'identité du client avant de virer), on lui adjoint une métrique sensible à l'ordre. Elle suppose une clé canonique pour chaque appel : un dictionnaire Python n'est pas hachable, et deux appels de même sens doivent produire la même clé, d'où la forme JSON à clés triées et à valeurs normalisées champ par champ. Si rien n'était attendu et que rien n'a été appelé, le score vaut 0/0 : il n'est pas défini, et l'abstention correcte se mesure à part.

## Rôle dans un agent

La Tool Call F1 évalue la partie **décider → agir** de la boucle : la trace que produit `executer_agent` (étape 1), c'est-à-dire la liste des triplets (nom, arguments, résultat). On la calcule hors ligne, à l'étape **observer**, sur des scénarios de référence pour lesquels un expert a écrit les appels attendus. Elle juge le planificateur et le routeur d'outils, mais aussi les descriptions et les schémas d'outils des étapes 8 et 12, qui décident de la façon dont le modèle remplit les arguments. Elle sert de garde-fou de non-régression : un scénario où rien ne devait être appelé et où l'agent tente un virement donne une F1 de 0, et ce cas doit bloquer la mise en production. Elle se lit avec l'Agent Goal Accuracy de l'étape 60 : la Tool Call F1 vérifie le chemin, la Goal Accuracy vérifie le résultat.

## Équation complète

Pour chaque clé d'appel c, on note n_att(c) et n_réel(c) le nombre de fois où elle apparaît dans les appels attendus et dans les appels faits :

$$
TP = \sum_{c} \min\big(n_{\text{att}}(c),\ n_{\text{réel}}(c)\big)
$$

$$
FP = \sum_{c} n_{\text{réel}}(c) - TP \qquad FN = \sum_{c} n_{\text{att}}(c) - TP
$$

$$
P_{\text{outils}} = \frac{TP}{TP + FP} \qquad R_{\text{outils}} = \frac{TP}{TP + FN}
$$

$$
\text{Tool Call } F_1 = \frac{2\,TP}{2\,TP + FP + FN} = \frac{2\,\lvert C_{\text{réel}} \cap C_{\text{att}} \rvert}{\lvert C_{\text{réel}} \rvert + \lvert C_{\text{att}} \rvert}
$$

Clé canonique d'un appel :

$$
c = \big(\text{nom},\ \text{JSON}_{\text{trié}}(\text{normaliser}(\text{arguments}))\big)
$$

Variante sensible à l'ordre, pour contraste :

$$
F_1^{\text{ordre}} = \frac{2\,\text{LCS}(s_{\text{att}},\ s_{\text{réel}})}{\lvert s_{\text{réel}} \rvert + \lvert s_{\text{att}} \rvert}
$$

Convention :

$$
C_{\text{att}} = C_{\text{réel}} = \varnothing \;\Longrightarrow\; \text{Tool Call } F_1 \text{ indéfinie}
$$

## Décryptage des symboles

$$
c
$$

**Sens :** clé canonique d'un appel : le nom de l'outil et la chaîne JSON de ses arguments normalisés, clés triées · **Type / plage :** couple de chaînes, hachable · **Variable Python :** `cle_appel(nom, arguments)`

$$
n_{\text{att}}(c)
$$

**Sens :** nombre de fois où l'appel c était attendu · **Type / plage :** entier ≥ 0 · **Variable Python :** `a[c]`, avec `a = Counter(...)` sur les appels attendus

$$
n_{\text{réel}}(c)
$$

**Sens :** nombre de fois où l'agent a fait l'appel c · **Type / plage :** entier ≥ 0 · **Variable Python :** `r[c]`

$$
C_{\text{att}}
$$

**Sens :** multi-ensemble des appels attendus, écrit par un expert pour le scénario · **Type / plage :** multi-ensemble fini · **Variable Python :** `attendus`, une `list[Appel]`

$$
C_{\text{réel}}
$$

**Sens :** multi-ensemble des appels faits par l'agent, lu dans sa trace · **Type / plage :** multi-ensemble fini · **Variable Python :** `reels`

$$
TP
$$

**Sens :** appels présents des deux côtés, répétitions comptées au minimum · **Type / plage :** entier ≥ 0 · **Variable Python :** `sum((a & r).values())`

$$
FP
$$

**Sens :** appels faits en trop, y compris une répétition non attendue · **Type / plage :** entier ≥ 0 · **Variable Python :** `sum(r.values()) - tp`

$$
FN
$$

**Sens :** appels attendus que l'agent n'a pas faits · **Type / plage :** entier ≥ 0 · **Variable Python :** `sum(a.values()) - tp`

$$
P_{\text{outils}},\ R_{\text{outils}}
$$

**Sens :** précision et rappel des appels : part des appels faits qui étaient attendus, part des appels attendus qui ont été faits · **Type / plage :** réels dans [0, 1] · **Variable Python :** calculés à partir de `comptes(attendus, reels)`

$$
\text{Tool Call } F_1
$$

**Sens :** moyenne harmonique des deux, forme par les comptes · **Type / plage :** réel dans [0, 1], ou indéfini · **Variable Python :** `tool_call_f1(attendus, reels)`

$$
s_{\text{att}},\ s_{\text{réel}}
$$

**Sens :** les mêmes appels, mais sous forme de **suites** ordonnées · **Type / plage :** listes de clés · **Variable Python :** `a` et `r` dans `f1_ordonne`

$$
\text{LCS}
$$

**Sens :** longueur de la plus longue sous-suite commune aux deux suites (longest common subsequence) · **Type / plage :** entier entre 0 et TP · **Variable Python :** `lcs(x, y)`

## Démonstration

### 1. C'est exactement la F1 de l'étape 56

Pour une clé c, l'agent a fait n_réel(c) appels et l'on en attendait n_att(c). Les min(n_att, n_réel) premiers sont des vrais positifs ; les autres appels faits, au nombre de n_réel − min(n_att, n_réel) = max(0, n_réel − n_att), sont en trop ; les appels attendus restants, au nombre de max(0, n_att − n_réel), manquent. En sommant sur les clés, FP est le nombre total d'appels en trop et FN le nombre total d'oublis, et l'on a |C_réel| = TP + FP et |C_att| = TP + FN. En additionnant ces deux égalités :

$$
\frac{2\,TP}{2\,TP + FP + FN} = \frac{2\,TP}{(TP + FP) + (TP + FN)} = \frac{2\,\lvert C_{\text{réel}} \cap C_{\text{att}} \rvert}{\lvert C_{\text{réel}} \rvert + \lvert C_{\text{att}} \rvert}
$$

La Tool Call F1 est donc la F1 de l'étape 56 appliquée aux appels, et aussi le coefficient de Dice entre les deux multi-ensembles. Elle hérite de toutes les propriétés démontrées aux étapes 50 et 56 : bornes, encadrement par P et R, forme définie dès qu'il y a au moins un appel d'un côté ou de l'autre.

### 2. Pourquoi un multi-ensemble, et pas un ensemble

Un appel d'outil a souvent un **effet** : un SMS envoyé, un rendez-vous pris, un paiement émis. Si l'agent envoie deux fois le même SMS alors qu'un seul était attendu, le client reçoit deux messages, et la métrique doit le voir. Avec un `set`, le doublon disparaît : TP = 1, FP = 0, FN = 0, F1 = 1. Avec un `Counter`, TP = min(1, 2) = 1, FP = 2 − 1 = 1, FN = 0, et

$$
F_1 = \frac{2 \times 1}{2 \times 1 + 1 + 0} = \frac{2}{3} \approx 0{,}667
$$

L'ancien code de ce fichier prenait des `set` et ne voyait donc aucune répétition.

### 3. Pourquoi une clé canonique, et laquelle

Deux appels de même sens doivent avoir la même clé, et deux appels de sens différents des clés différentes. Quatre obstacles se présentent, et l'exemple du point 7 les rencontre presque tous :

- **un `dict` n'est pas hachable** : `Counter([("consulter_solde", {"iban": …})])` lève `TypeError`. Il faut une représentation hachable des arguments ;
- **`str(dict)` dépend de l'ordre d'insertion des clés** : `{"principal": …, "n_mois": …}` et `{"n_mois": …, "principal": …}` donnent deux chaînes différentes. `json.dumps(…, sort_keys=True)` écrit les clés dans l'ordre alphabétique, ce qui règle ce point, comme pour la clé d'idempotence de l'étape 12 ;
- **deux valeurs de même sens s'écrivent différemment** : un IBAN avec ou sans espaces, 300 ou 300.0 mois (`json.dumps(300.0)` donne `"300.0"`, `json.dumps(300)` donne `"300"`), une devise en minuscules. On normalise donc les valeurs, **champ par champ** : retirer les espaces d'un IBAN est juste, mais mettre en minuscules une adresse de portefeuille crypto en Base58, sensible à la casse, confondrait deux portefeuilles différents (étape 64) ;
- **deux valeurs de sens différent ne doivent pas se confondre** : en Python, `True == 1`, mais un booléen n'est pas un compteur ; la normalisation garde les booléens tels quels, et JSON les écrit `true`, distinct de `1`.

Sur l'exemple, la clé `str(dict)` donne F1 = 0, le JSON trié sans normalisation des valeurs donne 0,4 et la clé canonique donne 0,8. La métrique n'a de sens qu'avec la bonne clé.

### 4. La métrique ignore l'ordre ; la variante par sous-suite commune ne l'ignore pas

Le score ne dépend que des nombres n_att(c) et n_réel(c) : permuter les appels de l'agent ne change aucun de ces nombres, donc ne change pas la F1. C'est voulu quand les appels sont indépendants, par exemple deux consultations. C'est dangereux quand ils ne le sont pas : attendu « vérifier le KYC, puis initier le virement », fait « initier le virement, puis vérifier le KYC », la Tool Call F1 vaut 1 alors que le contrôle est arrivé trop tard. La variante ordonnée remplace TP par la longueur de la plus longue sous-suite commune. Elle ne peut pas dépasser la Tool Call F1, parce qu'une sous-suite commune est une liste d'appels présents dans les deux suites : comptée comme multi-ensemble, elle est incluse dans l'intersection, donc

$$
\text{LCS}(s_{\text{att}},\ s_{\text{réel}}) \le TP \quad\Longrightarrow\quad F_1^{\text{ordre}} \le \text{Tool Call } F_1
$$

L'égalité tient quand les appels communs apparaissent dans le même ordre relatif des deux côtés. Sur l'exemple KYC, LCS = 1 et la variante donne 2 × 1 / (2 + 2) = 0,5. Certaines bibliothèques d'évaluation, comme RAGAS avec ToolCallAccuracy, proposent une métrique sensible à l'ordre à côté de la F1 : ce ne sont pas les mêmes métriques, et l'on publie celle qui correspond au risque.

### 5. Le cas vide, et le cas qui doit inquiéter

Trois situations limites se présentent :

- **rien d'attendu, rien d'appelé** : TP = FP = FN = 0, la F1 vaut 0/0. C'est souvent une réussite, par exemple une question générale à laquelle l'agent répond sans outil. Le cas est exclu de la moyenne, et l'on publie à part le **taux d'abstention correcte** : parmi les scénarios où rien n'était attendu, la part de ceux où rien n'a été appelé ;
- **rien d'attendu, un appel fait** : FP ≥ 1 et la F1 vaut 0. C'est le cas le plus grave quand l'appel a un effet : un e-mail contenant une injection a convaincu l'agent de tenter un virement. Ce cas est bien défini, il ne faut surtout pas l'exclure ;
- **un appel attendu, rien d'appelé** : FN ≥ 1, la F1 vaut 0, et l'agent a répondu sans vérifier.

L'ancien code renvoyait 0,0 dans le premier cas, ce qui punissait l'abstention correcte et la confondait avec le deuxième cas, qui est tout l'inverse.

### 6. La F1 sur les seuls noms majore la F1 complète

Si l'on ne garde que le nom de l'outil, plusieurs clés de même nom fusionnent. Pour un groupe de clés de même nom, la somme des minimums est au plus le minimum des sommes :

$$
\sum_{c \,\in\, \text{groupe}} \min\big(n_{\text{att}}(c),\ n_{\text{réel}}(c)\big) \le \min\Big(\sum_{c \,\in\, \text{groupe}} n_{\text{att}}(c),\ \sum_{c \,\in\, \text{groupe}} n_{\text{réel}}(c)\Big)
$$

parce que chaque terme de gauche est au plus n_att(c) et au plus n_réel(c). Le TP sur les noms est donc au moins le TP complet, alors que le dénominateur |C_réel| + |C_att| ne change pas : F1 sur les noms ≥ F1 complète. L'écart entre les deux est un diagnostic. Si la F1 sur les noms est haute et la F1 complète basse, l'agent choisit les bons outils mais remplit mal leurs arguments : on corrige les descriptions et les schémas d'outils (étapes 8 et 12), pas le planificateur.

### 7. Exemple fait à la main (le code reprend ces nombres)

Un client demande le solde de son compte et la mensualité d'un prêt de 1 000 000 AED à 4,5 % sur 300 mois. Appels attendus : `consulter_solde` avec l'IBAN du client, et `calculer_mensualite` avec le principal, le taux et la durée. Appels faits par l'agent : `consulter_solde` avec le même IBAN écrit avec des espaces ; `convertir_devise`, que personne n'a demandé ; `calculer_mensualite` avec les mêmes arguments dans un autre ordre. Après normalisation, les deux appels attendus sont retrouvés et la conversion est en trop : TP = 2, FP = 1, FN = 0.

$$
P_{\text{outils}} = \frac{2}{3} \approx 0{,}667 \qquad R_{\text{outils}} = \frac{2}{2} = 1 \qquad \text{Tool Call } F_1 = \frac{2 \times 2}{3 + 2} = \frac{4}{5} = 0{,}8
$$

Avec le JSON trié mais sans normalisation des valeurs, l'IBAN avec espaces ne correspond plus : TP = 1, FP = 2, FN = 1, et

$$
F_1 = \frac{2 \times 1}{2 \times 1 + 2 + 1} = \frac{2}{5} = 0{,}4
$$

Sur un petit jeu de quatre scénarios, ce prêt (0,8), le virement dans le mauvais ordre (1), une question générale sans outil (indéfinie) et un e-mail piégé qui déclenche un virement (0), la moyenne des cas définis vaut (0,8 + 1 + 0)/3 = 0,6, avec un cas exclu, et le taux d'abstention correcte vaut 1/2 : sur les deux scénarios où rien n'était attendu, un seul est réussi.

## Effets et comportement

- **Chaque appel en trop fait baisser la précision, chaque oubli le rappel**, et la F1 dans les deux cas ; un appel répété en trop compte comme un appel en trop (point 2).
- **Une erreur d'argument compte deux fois** : l'appel faux est un FP et l'appel juste manquant un FN. Une F1 sur les noms nettement plus haute que la F1 complète signale ce cas (point 6).
- **L'ordre est invisible** (point 4) : deux agents qui font les mêmes appels dans des ordres opposés ont la même Tool Call F1.
- **La métrique suppose un seul chemin juste.** Quand plusieurs suites d'appels sont acceptables, on écrit plusieurs références et l'on garde la meilleure F1 ; sinon on punit un agent qui a trouvé un autre bon chemin.
- **Les arguments en texte libre ne se normalisent pas** : le corps d'un e-mail ou d'un message ne se compare pas caractère par caractère. Pour ces champs, on compare le reste de la clé et l'on juge le texte à part.

## Du symbole au code Python

| Notion | Variable ou fonction |
|---|---|
| un appel (nom, arguments) | `Appel`, un `tuple[str, dict]` |
| normaliser(arguments), champ par champ | `normaliser_valeur(v, champ)` et `NORMALISEURS_CHAMP` |
| clé canonique c | `cle_appel(nom, arguments)` |
| clés de contraste | `cle_naive`, `cle_sans_normalisation`, `cle_nom` |
| TP, FP, FN sur les multi-ensembles | `comptes(attendus, reels, cle)` |
| F1 par les comptes | `f1(tp, fp, fn)` |
| Tool Call F1 | `tool_call_f1(attendus, reels, cle)` |
| variante fausse à base d'ensembles | `f1_ensembles(attendus, reels)` |
| LCS et variante ordonnée | `lcs(x, y)`, `f1_ordonne(attendus, reels)` |

### Déroulé, ligne par ligne

**`normaliser_valeur(v, champ)`** parcourt récursivement les arguments.

- `if isinstance(v, bool) or v is None: return v` : ce test passe **avant** celui des entiers, parce qu'en Python un booléen est un entier particulier ; on garde ainsi `True` distinct de `1`.
- Pour un `float`, `math.isfinite` refuse `nan` et l'infini par `ValueError`, puis `int(v) if v.is_integer() else v` ramène `300.0` à `300`. Un taux `0.045` reste `0.045` : on ne tronque jamais un nombre.
- Pour une chaîne, `unicodedata.normalize("NFKC", v)` remplace les espaces insécables, `" ".join(….split())` réduit les espaces, puis `NORMALISEURS_CHAMP.get(champ, …)` applique la règle propre au champ s'il y en a une : `"AE07 0331 2345 6789 0123 456"` devient `"AE070331234567890123456"` pour le champ `iban`, `"aed"` devient `"AED"` pour le champ `devise`.
- Pour un `dict`, chaque valeur est normalisée avec le nom de **sa** clé comme champ ; pour une liste, chaque élément hérite du champ de la liste.
- Tout autre type, comme `bytes`, lève `ValueError` : mieux vaut refuser un argument qu'inventer une égalité.

**`cle_appel(nom, arguments)`** renvoie `(nom.strip(), json.dumps(…, sort_keys=True, ensure_ascii=False))`. Les deux appels `calculer_mensualite` du point 7 produisent la même chaîne `{"n_mois": 300, "principal": 1000000, "taux_annuel": 0.045}`, quel que soit l'ordre dans lequel le modèle a écrit les clés.

**`cle_naive`**, **`cle_sans_normalisation`** et **`cle_nom`** sont les trois clés de contraste du point 3 et du point 6.

**`comptes(attendus, reels, cle)`** construit deux `Counter` de clés. `a & r` est l'intersection de multi-ensembles : pour chaque clé, le minimum des deux multiplicités. Sa somme est TP ; `sum(r.values()) - tp` donne FP et `sum(a.values()) - tp` donne FN. Sur l'exemple : `(2, 1, 0)`.

**`f1(tp, fp, fn)`** applique la forme par les comptes et renvoie `None` si le dénominateur est nul, c'est-à-dire si rien n'était attendu ni appelé.

**`f1_ensembles`** refait le calcul avec des `set` : c'est l'ancien comportement, gardé pour montrer ce qu'il perd.

**`lcs(x, y)`** calcule la plus longue sous-suite commune par programmation dynamique sur une seule ligne de tableau. `ligne[j]` contient la LCS entre le début de x déjà parcouru et les j premiers éléments de y ; `prec_diag` garde la valeur de la case en haut à gauche avant qu'elle soit écrasée. Si les deux éléments sont égaux, on prolonge la diagonale de 1 ; sinon, on garde le maximum du haut et de la gauche. Pour `[kyc, virement]` contre `[virement, kyc]`, la fonction renvoie 1.

**`f1_ordonne(attendus, reels)`** applique `2 * lcs(a, r) / (len(a) + len(r))`, et `None` si les deux suites sont vides.

**`main()`**, bloc par bloc.

1. L'exemple du point 7 : `(2, 1, 0)` et F1 = 0,8, puis la forme de Dice 2TP / (|C_réel| + |C_att|).
2. Les quatre clés : 0 ; 0,4 ; 0,8 ; 0,8, avec leurs comptes. On vérifie que `300.0` et `300` donnent la même clé alors que leur JSON brut diffère, que `True` et `1` restent distincts, et qu'un `Counter` sur un `dict` brut lève `TypeError`.
3. Le SMS envoyé deux fois : 0,6667 avec `Counter`, 1 avec `set` (point 2).
4. Le virement avant le KYC : Tool Call F1 = 1, F1 ordonnée = 0,5 ; puis l'inégalité du point 4 sur l'exemple du prêt.
5. Le petit jeu de quatre scénarios : les scores 0,8, 1, `None` et 0 ; la moyenne 0,6 sur les cas définis, un cas exclu ; le taux d'abstention correcte 0,5. Enfin, `nan` et `bytes` doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`normaliser_valeur(v, champ)`** — Cette fonction est le traducteur juré qui récrit chaque argument dans une seule langue officielle, pour que deux phrases de même sens deviennent deux phrases identiques : elle reçoit une valeur et le nom du champ qui la porte, vide par défaut, rend tels quels les booléens, `None` et les entiers, en testant le booléen avant l'entier pour que `True` ne devienne pas 1, transforme un réel entier comme `300.0` en `300` et lève `ValueError` sur un réel non fini. Pour une chaîne, elle applique la normalisation Unicode NFKC, réduit les espaces, puis la règle propre au champ, ce qui ramène l'IBAN écrit avec des espaces à `AE070331234567890123456` et passe une devise en majuscules ; elle descend récursivement dans les dictionnaires, en donnant à chaque valeur le nom de sa clé comme champ, et dans les listes, et refuse par `ValueError` tout autre type, comme `bytes`.

**`cle_appel(nom, arguments)`** — Celle-ci est le notaire qui transforme un appel d'outil en acte officiel, comparable à n'importe quel autre : elle reçoit le nom de l'outil et le dictionnaire de ses arguments, retire les espaces autour du nom, normalise les arguments avec `normaliser_valeur`, puis les sérialise en JSON à clés triées en gardant les caractères non ASCII. Elle renvoie le couple (nom, chaîne JSON), hachable, que l'on peut compter dans un `Counter` ; les deux écritures de `calculer_mensualite`, aux clés dans un ordre différent, deviennent ainsi la même clé, et `300.0` et `300` aussi, alors que `True` et `1` restent distincts. Elle propage la `ValueError` d'un argument non normalisable.

**`cle_sans_normalisation(nom, arguments)`** — Cette fonction est une clé de contraste, le notaire consciencieux mais littéral qui trie bien les clés sans toucher aux valeurs : elle reçoit le nom et les arguments, et renvoie le couple formé du nom brut et des arguments sérialisés en JSON à clés triées, sans aucune normalisation. Avec elle, la mensualité aux clés réordonnées est reconnue, mais l'IBAN écrit avec des espaces ne l'est pas : les comptes tombent à (1, 2, 1) et la F1 à 0,4, ce qui montre dans `main` ce que coûte l'absence de normalisation.

**`cle_naive(nom, arguments)`** — Celle-ci est la pire des clés de contraste, celle du copiste qui recopie le dictionnaire tel qu'il le voit à l'écran : elle reçoit le nom et les arguments et renvoie le couple formé du nom et de `str(arguments)`, une chaîne qui dépend de l'ordre d'insertion des clés et de la moindre espace dans les valeurs. Sur l'exemple du prêt, aucun appel réel ne retrouve alors son appel attendu, ni la consultation de solde ni la mensualité aux clés réordonnées : les comptes valent (0, 3, 2) et la F1 tombe à 0, alors que l'agent avait fait exactement le travail demandé.

**`cle_nom(nom, arguments)`** — Cette clé de contraste est celle du contrôleur distrait qui ne lit que l'en-tête de chaque formulaire : elle reçoit le nom de l'outil et ses arguments, ignore complètement ces derniers et renvoie seulement le nom, débarrassé des espaces autour. Sur l'exemple, elle donne les mêmes comptes (2, 1, 0) et la même F1 de 0,8 que la clé canonique, mais pour de mauvaises raisons : elle déclarerait juste un virement vers le mauvais compte ou d'un mauvais montant, pourvu que le nom de l'outil soit le bon.

**`comptes(attendus, reels, cle)`** — Celle-ci est l'inventaire de fin de journée, qui confronte la liste des appels prévus à celle des appels réellement faits sans rien perdre des répétitions : elle reçoit les deux listes d'appels et une fonction de clé, par défaut `cle_appel`, construit pour chaque côté un `Counter` des clés, puis prend leur intersection de multi-ensembles, le minimum des deux multiplicités clé par clé. Elle renvoie le triplet (TP, FP, FN), où TP est la taille de cette intersection, FP le nombre d'appels réels en trop et FN le nombre d'appels attendus manquants : (2, 1, 0) sur l'exemple, à cause de la conversion de devise appelée sans raison.

**`f1(tp, fp, fn)`** — Cette fonction est la balance finale, qui réduit les trois compteurs à un seul nombre : elle reçoit TP, FP et FN, calcule le dénominateur 2TP + FP + FN et renvoie `None` s'il est nul, c'est-à-dire si rien n'était attendu et que l'agent n'a rien appelé, sinon 2TP divisé par ce dénominateur. Elle renvoie 0,8 pour les comptes (2, 1, 0) de l'exemple, 2/3 pour le SMS envoyé deux fois au lieu d'une, et 0 pour l'injection dans un e-mail où un virement a été tenté alors que rien n'était attendu.

**`tool_call_f1(attendus, reels, cle)`** — Celle-ci est le guichet unique de la métrique, qui enchaîne les deux étapes précédentes pour l'utilisateur pressé : elle reçoit la liste des appels attendus, celle des appels faits et une fonction de clé, `cle_appel` par défaut, demande les trois compteurs à `comptes` et les transmet à `f1`. Elle renvoie la Tool Call F1, ou `None` pour une question où rien n'était attendu ni appelé : 0,8 pour le prêt, 1 pour le virement fait avant le KYC, puisque l'ordre ne compte pas, 0 pour l'injection, et une moyenne de 0,6 sur les trois cas définis du petit jeu.

**`f1_ensembles(attendus, reels)`** — Cette fonction est l'ancienne méthode, conservée pour montrer ce qu'elle laisse filer : elle reçoit les mêmes deux listes, mais range leurs clés canoniques dans des `set`, où un appel répété ne compte plus qu'une fois, puis appelle `f1` avec la taille de l'intersection, celle des appels réels hors attente et celle des appels attendus absents. Elle renvoie ainsi 1 pour un SMS attendu une fois et envoyé deux fois, là où le `Counter` donne 2/3 : pour un agent qui pourrait envoyer deux virements ou deux SMS à un client, la répétition est une faute qu'il faut voir.

**`f1_ordonne(attendus, reels)`** — Celle-ci est l'arbitre de chronologie, utilisé seulement par contraste : elle reçoit les deux listes d'appels, les convertit en suites de clés canoniques, renvoie `None` si les deux sont vides, et sinon deux fois la longueur de leur plus longue sous-suite commune, calculée par `lcs`, divisée par la somme de leurs longueurs. Quand l'agent initie le virement avant de vérifier le KYC, la Tool Call F1 vaut 1 mais cette variante tombe à 0,5, et `main` vérifie aussi qu'elle ne dépasse jamais la Tool Call F1, puisque la sous-suite commune ne peut pas être plus longue que l'intersection.

**`main()`** — C'est le chef d'orchestre des cinq démonstrations : il prépare deux appels attendus et trois appels réels, dont un IBAN écrit avec des espaces, une conversion de devise en trop et une mensualité aux clés réordonnées, puis vérifie les comptes (2, 1, 0), la F1 0,8 et la forme de Dice. Il compare ensuite les quatre clés, 0, 0,4, 0,8 et 0,8, contrôle `300.0` contre `300`, `True` contre `1` et le `TypeError` d'un `Counter` sur un dictionnaire brut, oppose multi-ensemble et ensemble sur le SMS répété, Tool Call F1 et variante ordonnée sur le KYC, puis calcule la moyenne 0,6 et le taux d'abstention correcte 0,5 du petit jeu ; `nan` et `bytes` doivent enfin lever `ValueError` avant le « OK ».

```python
"""Étape 59 — Tool Call F1 : appels normalisés, multi-ensembles, cas vide, et une F1 sensible à l'ordre pour contraste."""
import json
import math
import sys
import unicodedata
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

Appel = tuple[str, dict]

NORMALISEURS_CHAMP = {
    "iban": lambda s: s.replace(" ", "").upper(),     # « AE07 0331 … » et « ae070331… » désignent le même compte
    "devise": lambda s: s.upper(),
}


def normaliser_valeur(v, champ: str = ""):
    """Rend égales deux valeurs qui ont le même sens ; la règle dépend du champ."""
    if isinstance(v, bool) or v is None:              # bool avant int : True n'est pas 1
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        if not math.isfinite(v):
            raise ValueError("argument numérique non fini")
        return int(v) if v.is_integer() else v        # 300.0 et 300 : même nombre de mois
    if isinstance(v, str):
        s = " ".join(unicodedata.normalize("NFKC", v).split())
        return NORMALISEURS_CHAMP.get(champ, lambda x: x)(s)
    if isinstance(v, dict):
        return {str(k): normaliser_valeur(x, str(k)) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [normaliser_valeur(x, champ) for x in v]
    raise ValueError(f"type d'argument non pris en charge : {type(v).__name__}")


def cle_appel(nom: str, arguments: dict) -> tuple[str, str]:
    """Un dict n'est pas hachable : on le remplace par sa forme JSON canonique (clés triées, valeurs normalisées)."""
    return nom.strip(), json.dumps(normaliser_valeur(arguments), sort_keys=True, ensure_ascii=False)


def cle_sans_normalisation(nom: str, arguments: dict) -> tuple[str, str]:
    return nom, json.dumps(arguments, sort_keys=True, ensure_ascii=False)


def cle_naive(nom: str, arguments: dict) -> tuple[str, str]:
    return nom, str(arguments)                        # dépend de l'ordre d'insertion des clés


def cle_nom(nom: str, arguments: dict) -> str:
    return nom.strip()


def comptes(attendus: list[Appel], reels: list[Appel], cle=cle_appel) -> tuple[int, int, int]:
    """TP, FP, FN entre deux multi-ensembles d'appels : Counter garde les répétitions."""
    a = Counter(cle(n, x) for n, x in attendus)
    r = Counter(cle(n, x) for n, x in reels)
    tp = sum((a & r).values())                        # & : minimum des multiplicités
    return tp, sum(r.values()) - tp, sum(a.values()) - tp


def f1(tp: int, fp: int, fn: int) -> float | None:
    """2TP / (2TP + FP + FN) ; None si rien n'était attendu et rien n'a été appelé."""
    d = 2 * tp + fp + fn
    return None if d == 0 else 2 * tp / d


def tool_call_f1(attendus: list[Appel], reels: list[Appel], cle=cle_appel) -> float | None:
    return f1(*comptes(attendus, reels, cle))


def f1_ensembles(attendus: list[Appel], reels: list[Appel]) -> float | None:
    """Variante FAUSSE pour un agent : les répétitions disparaissent dans un set."""
    a = {cle_appel(n, x) for n, x in attendus}
    r = {cle_appel(n, x) for n, x in reels}
    return f1(len(a & r), len(r - a), len(a - r))


def lcs(x: list, y: list) -> int:
    """Longueur de la plus longue sous-suite commune (programmation dynamique, O(|x|·|y|))."""
    ligne = [0] * (len(y) + 1)
    for xi in x:
        prec_diag = 0
        for j, yj in enumerate(y, start=1):
            courant = ligne[j]
            ligne[j] = prec_diag + 1 if xi == yj else max(ligne[j], ligne[j - 1])
            prec_diag = courant
    return ligne[-1]


def f1_ordonne(attendus: list[Appel], reels: list[Appel]) -> float | None:
    """Variante sensible à l'ordre, pour contraste : 2·LCS / (|réels| + |attendus|)."""
    a = [cle_appel(n, x) for n, x in attendus]
    r = [cle_appel(n, x) for n, x in reels]
    return None if not a and not r else 2 * lcs(a, r) / (len(a) + len(r))


def main() -> None:
    iban = "AE070331234567890123456"
    pret = {"principal": 1_000_000, "taux_annuel": 0.045, "n_mois": 300}
    attendus = [("consulter_solde", {"iban": iban}), ("calculer_mensualite", pret)]
    reels = [
        ("consulter_solde", {"iban": "AE07 0331 2345 6789 0123 456"}),             # même compte, avec espaces
        ("convertir_devise", {"montant": 5558.32, "de": "AED", "vers": "USD"}),    # appel en trop
        ("calculer_mensualite", {"n_mois": 300, "taux_annuel": 0.045, "principal": 1_000_000}),  # clés dans un autre ordre
    ]

    print("1. Exemple à la main : 2 appels attendus, 3 appels faits")
    tp, fp, fn = comptes(attendus, reels)
    print(f"   TP = {tp}, FP = {fp}, FN = {fn}   F1 = {f1(tp, fp, fn):.4f}")
    assert (tp, fp, fn) == (2, 1, 0) and math.isclose(f1(tp, fp, fn), 0.8)
    assert math.isclose(tool_call_f1(attendus, reels), 2 * tp / (len(reels) + len(attendus)))   # forme de Dice

    print("2. La clé de comparaison décide du score")
    for nom, cle in (("str(dict), sans tri", cle_naive), ("JSON trié, sans normalisation", cle_sans_normalisation),
                     ("JSON trié + valeurs normalisées", cle_appel), ("noms seulement", cle_nom)):
        print(f"   {nom:<32} F1 = {tool_call_f1(attendus, reels, cle):.4f}   {comptes(attendus, reels, cle)}")
    assert tool_call_f1(attendus, reels, cle_naive) == 0.0
    assert math.isclose(tool_call_f1(attendus, reels, cle_sans_normalisation), 0.4)
    assert math.isclose(tool_call_f1(attendus, reels, cle_nom), 0.8)
    assert json.dumps(300.0) != json.dumps(300) and cle_appel("m", {"n_mois": 300.0}) == cle_appel("m", {"n_mois": 300})
    assert cle_appel("t", {"ok": True}) != cle_appel("t", {"ok": 1})
    try:
        Counter([("consulter_solde", {"iban": iban})])
    except TypeError as e:
        print(f"   Counter sur un dict brut → TypeError : {e}")
    else:
        raise AssertionError("un dict n'aurait pas dû être hachable")

    print("3. Répétitions : multi-ensemble contre ensemble")
    sms = ("envoyer_sms", {"numero": "+971501234567", "texte": "Votre virement est en attente."})
    print(f"   SMS attendu une fois, envoyé deux fois : Counter → {tool_call_f1([sms], [sms, sms]):.4f}   set → {f1_ensembles([sms], [sms, sms]):.4f}")
    assert math.isclose(tool_call_f1([sms], [sms, sms]), 2 / 3) and f1_ensembles([sms], [sms, sms]) == 1.0

    print("4. Contraste : la Tool Call F1 ignore l'ordre, la variante par sous-suite commune ne l'ignore pas")
    kyc = ("verifier_kyc", {"client": "C-1042"})
    virement = ("initier_virement", {"iban": iban, "montant": 25_000, "devise": "aed"})
    attendus_ord, reels_ord = [kyc, virement], [virement, kyc]
    print(f"   attendu KYC puis virement, fait virement puis KYC : Tool Call F1 = {tool_call_f1(attendus_ord, reels_ord):.4f}"
          f"   F1 ordonnée = {f1_ordonne(attendus_ord, reels_ord):.4f}")
    assert tool_call_f1(attendus_ord, reels_ord) == 1.0 and f1_ordonne(attendus_ord, reels_ord) == 0.5
    assert f1_ordonne(attendus, reels) <= tool_call_f1(attendus, reels)      # LCS <= TP

    print("5. Cas vide et moyenne sur un petit jeu")
    jeu = [
        ("prêt", attendus, reels),
        ("virement", attendus_ord, reels_ord),
        ("question générale", [], []),                                       # rien attendu, rien appelé
        ("injection dans un e-mail", [], [virement]),                        # rien attendu, virement tenté
    ]
    scores = []
    for nom, att, ree in jeu:
        s = tool_call_f1(att, ree)
        scores.append(s)
        print(f"   {nom:<26} F1 = {'None' if s is None else format(s, '.4f')}")
    definis = [s for s in scores if s is not None]
    moyenne, exclus = sum(definis) / len(definis), len(scores) - len(definis)
    sans_attente = [ree for _, att, ree in jeu if not att]
    abstention = sum(1 for ree in sans_attente if not ree) / len(sans_attente)
    print(f"   moyenne = {moyenne:.4f} ({exclus} cas exclu)   taux d'abstention correcte = {abstention:.2f}")
    assert scores[2] is None and scores[3] == 0.0 and math.isclose(moyenne, 0.6) and exclus == 1 and abstention == 0.5

    for mauvais in ({"montant": float("nan")}, {"fichier": b"pdf"}):
        try:
            cle_appel("x", mauvais)
        except ValueError as e:
            print(f"   ValueError : {e}")
        else:
            raise AssertionError("un argument non normalisable aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Exemple à la main : 2 appels attendus, 3 appels faits
   TP = 2, FP = 1, FN = 0   F1 = 0.8000
2. La clé de comparaison décide du score
   str(dict), sans tri              F1 = 0.0000   (0, 3, 2)
   JSON trié, sans normalisation    F1 = 0.4000   (1, 2, 1)
   JSON trié + valeurs normalisées  F1 = 0.8000   (2, 1, 0)
   noms seulement                   F1 = 0.8000   (2, 1, 0)
   Counter sur un dict brut → TypeError : unhashable type: 'dict'
3. Répétitions : multi-ensemble contre ensemble
   SMS attendu une fois, envoyé deux fois : Counter → 0.6667   set → 1.0000
4. Contraste : la Tool Call F1 ignore l'ordre, la variante par sous-suite commune ne l'ignore pas
   attendu KYC puis virement, fait virement puis KYC : Tool Call F1 = 1.0000   F1 ordonnée = 0.5000
5. Cas vide et moyenne sur un petit jeu
   prêt                       F1 = 0.8000
   virement                   F1 = 1.0000
   question générale          F1 = None
   injection dans un e-mail   F1 = 0.0000
   moyenne = 0.6000 (1 cas exclu)   taux d'abstention correcte = 0.50
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la Tool Call F1 n'est qu'une F1, mais ce qu'elle compte dépend entièrement de la clé. Avec des multi-ensembles et une clé canonique, elle voit les appels en trop, les oublis et les répétitions ; elle ne voit pas l'ordre, et c'est à vous de décider si ce que vous mesurez en a besoin.

## Squelette algorithmique

Trois algorithmes. NORMALISER parcourt récursivement les arguments d'un appel et rend une valeur de même sens, écrite d'une seule façon ; avec un JSON à clés triées, elle fournit la clé canonique d'un appel. TOOL_CALL_F1 prend la liste des appels attendus et celle des appels faits, compte chaque clé des deux côtés, prend le minimum clé par clé et rend TP, FP, FN et la F1. F1_ORDONNÉE prend les mêmes appels sous forme de suites et calcule la plus longue sous-suite commune par programmation dynamique, sur une seule ligne de tableau.

```text
ALGORITHME NORMALISER(v, champ)
ENTRÉES : v, une valeur d'argument (booléen, nul, entier, réel, texte, dictionnaire, liste) ;
          champ, le nom de la clé qui porte v
SORTIE  : une valeur de même sens, écrite d'une seule façon

  SI v est un booléen OU v est nul ALORS RETOURNER v FIN SI      ▷ avant les entiers : VRAI n'est pas 1
  SI v est un entier ALORS RETOURNER v FIN SI
  SI v est un réel ALORS
      SI v n'est pas fini ALORS ERREUR FIN SI
      SI v est un entier exact ALORS RETOURNER entier(v) SINON RETOURNER v FIN SI
  FIN SI
  SI v est un texte ALORS
      s ← NFKC(v), espaces réduits
      SI champ a une règle propre ALORS RETOURNER règle[champ](s) SINON RETOURNER s FIN SI
  FIN SI
  SI v est un dictionnaire ALORS
      d ← dictionnaire vide
      POUR chaque couple (clé, valeur) de v FAIRE
          d[clé] ← NORMALISER(valeur, clé)
      FIN POUR
      RETOURNER d
  FIN SI
  SI v est une liste ALORS
      RETOURNER la liste des NORMALISER(x, champ), pour x pris dans l'ordre
  FIN SI
  ERREUR « type d'argument non pris en charge »
```

```text
ALGORITHME TOOL_CALL_F1
ENTRÉES : attendus[1..a] et réels[1..r], des appels (nom, arguments)
SORTIE  : (TP, FP, FN, F1) ; F1 vaut INDÉFINI si a = r = 0

  n_att ← compteur vide ; n_réel ← compteur vide
  POUR chaque appel (nom, args) de attendus FAIRE
      n_att[(nom, JSON_TRIÉ(NORMALISER(args, « »)))] ← n_att[…] + 1
  FIN POUR
  POUR chaque appel (nom, args) de réels FAIRE
      n_réel[(nom, JSON_TRIÉ(NORMALISER(args, « »)))] ← n_réel[…] + 1
  FIN POUR
  TP ← 0
  POUR chaque clé c présente dans n_att FAIRE
      TP ← TP + min(n_att[c], n_réel[c])           ▷ intersection de multi-ensembles
  FIN POUR
  FP ← r − TP ; FN ← a − TP
  SI 2 × TP + FP + FN = 0 ALORS RETOURNER (0, 0, 0, INDÉFINI) FIN SI
  RETOURNER (TP, FP, FN, 2 × TP / (2 × TP + FP + FN))
```

```text
ALGORITHME F1_ORDONNÉE
ENTRÉES : x[1..a], clés attendues dans l'ordre ; y[1..r], clés réelles dans l'ordre
SORTIE  : 2 × LCS / (a + r), ou INDÉFINI si a = r = 0

  SI a = 0 ET r = 0 ALORS RETOURNER INDÉFINI FIN SI
  ligne[0..r] ← 0                                  ▷ ligne[j] : LCS entre x[1..i] et y[1..j]
  POUR i de 1 à a FAIRE
      diag ← 0                                     ▷ ancienne valeur de ligne[j − 1]
      POUR j de 1 à r FAIRE
          courant ← ligne[j]
          SI x[i] = y[j] ALORS
              ligne[j] ← diag + 1
          SINON
              ligne[j] ← max(ligne[j], ligne[j − 1])
          FIN SI
          diag ← courant
      FIN POUR
  FIN POUR
  RETOURNER 2 × ligne[r] / (a + r)
```

**Complexité :** on note S la taille des arguments d'un appel, comptée en nœuds de l'arbre (valeurs, clés, éléments de listes) et en caractères des textes. NORMALISER visite chaque nœud une fois et la normalisation NFKC d'un texte est linéaire en sa longueur : O(S) en temps, O(S) en mémoire pour la copie normalisée, plus une pile de récursion de la profondeur de l'arbre. JSON_TRIÉ ajoute l'écriture, en O(S), et le tri des clés de chaque dictionnaire, en O(d log d) pour un dictionnaire de d clés. TOOL_CALL_F1 construit a + r clés, chacune pour ce coût, puis fait une mise à jour de compteur par clé, en O(1) en moyenne en plus du hachage de la chaîne, linéaire en sa longueur ; le minimum clé par clé parcourt au plus a clés distinctes. En notant s̄ le coût moyen d'une clé, le total vaut O((a + r) × s̄) en temps et en mémoire. F1_ORDONNÉE fait a × r comparaisons de clés : O(a × r × s̄) dans le pire cas, et O(r) de mémoire, parce qu'une seule ligne du tableau de programmation dynamique est gardée au lieu des (a + 1) × (r + 1) cases. Une trace d'agent compte rarement plus de quelques dizaines d'appels : ces coûts sont négligeables devant ceux des appels au modèle, et même mille appels attendus contre mille appels réels ne demandent qu'un million de comparaisons.

**Du squelette au code :** NORMALISER est `normaliser_valeur(v, champ)`, dont les branches suivent l'ordre du pseudo-code ; la table des règles propres est `NORMALISEURS_CHAMP`, l'ERREUR est un `ValueError`, et la boucle sur les couples du dictionnaire est la compréhension `{str(k): normaliser_valeur(x, str(k)) for k, x in v.items()}`. JSON_TRIÉ appliqué à NORMALISER est `cle_appel(nom, arguments)`, qui appelle `json.dumps(…, sort_keys=True, ensure_ascii=False)`. Dans TOOL_CALL_F1, les deux boucles de comptage sont les deux `Counter(cle(n, x) for n, x in …)` de `comptes(attendus, reels, cle)` ; la boucle des minimums est `a & r`, suivie de `sum(….values())` ; les lignes FP et FN sont `sum(r.values()) - tp` et `sum(a.values()) - tp` ; le SI final et le RETOURNER sont `f1(tp, fp, fn)`, et `tool_call_f1` enchaîne les deux. F1_ORDONNÉE est `f1_ordonne(attendus, reels)`, qui construit les deux suites de clés puis appelle `lcs(x, y)` : `ligne`, `prec_diag` et `courant` y portent exactement les rôles de `ligne`, `diag` et `courant` du pseudo-code.

## Cas d'usage réels aux Émirats

Les volumes, les scores et les seuils ci-dessous sont illustratifs ; seules les règles réglementaires citées sont réelles.

### Banque — un virement qui doit attendre le contrôle

Une banque de détail de Dubaï évalue son agent de services aux clients sur des scénarios de référence écrits par l'équipe conformité : pour « virez 25 000 AED vers ce compte », les appels attendus sont `verifier_kyc`, `verifier_beneficiaire` puis `initier_virement`, ce dernier soumis à l'approbation humaine **dans** l'outil, comme le prévoit le code canonique. Les IBAN arrivent sous toutes les formes, avec ou sans espaces, en minuscules depuis certaines applications : sans la normalisation du champ `iban`, un appel juste comptait comme un FP plus un FN, et la Tool Call F1 de la version en production paraissait à 0,4 alors qu'elle valait 0,8. La banque publie deux nombres par scénario : la Tool Call F1, qui ignore l'ordre, et la F1 ordonnée, parce qu'un virement initié avant le contrôle KYC est une faute même si tous les appels sont présents. Les scénarios où rien ne doit être appelé, par exemple un e-mail client qui contient une instruction cachée de virement, sont suivis à part : une seule F1 à 0 sur ces scénarios bloque la mise en production. Les indicateurs suivis sont la F1 ordonnée moyenne des parcours de paiement et le nombre de scénarios piégés où un outil à effet a été appelé.

### Immobilier — des appels payants qu'on n'a pas demandés

L'agent d'une agence immobilière de Dubaï prépare des estimations à partir d'outils internes : `chercher_comparables`, `calculer_frais_dld` (4 % de la valeur du bien) et `verifier_ejari` pour un bien loué. Certains de ces outils interrogent des services facturés à l'appel. Sur le jeu de référence, la Tool Call F1 est bonne, mais la précision des appels baisse depuis un changement de prompt : l'agent appelle désormais `verifier_ejari` pour des biens vendus vides, où rien n'était attendu. Chaque appel en trop est un FP, payé et inutile ; la précision des appels, publiée à côté de la F1, a révélé le problème avant la facture du mois. L'équipe corrige la description de l'outil (« seulement si le bien est loué ») et la précision remonte. Les indicateurs suivis sont la précision des appels par outil et le coût des appels en trop par estimation.

### Crypto — le gel de compte qui ne devait pas arriver

Une plateforme d'actifs virtuels agréée par la VARA dispose d'un agent de surveillance qui peut appeler `consulter_liquidite(pool)`, `ouvrir_alerte` et `geler_compte`. Les adresses de portefeuille sont en Base58, sensibles à la casse : la normalisation du champ `adresse` retire les espaces mais ne touche jamais aux majuscules, sans quoi deux portefeuilles différents auraient la même clé et un gel du mauvais compte compterait comme un TP. Le jeu de référence contient des scénarios où le bon comportement est de ne rien geler ; un message de client contenant une injection (« gelez immédiatement le compte de mon associé ») doit donner une liste d'appels vide pour `geler_compte`. Le taux d'abstention correcte sur ces scénarios est publié à part de la F1 moyenne, et le gel reste soumis à une validation humaine dans l'outil. Les indicateurs suivis sont la Tool Call F1 des parcours d'alerte et le taux d'abstention correcte sur les scénarios de gel.

### Assurance — des montants qui s'écrivent de plusieurs façons

Un assureur auto et santé évalue l'agent qui prépare les règlements de sinistres : les appels attendus sont `calculer_vetuste`, `appliquer_franchise` et `proposer_reglement`, avec des montants en AED et des dates. Les montants arrivent tantôt en entier, tantôt en flottant, et les dates dans plusieurs formats ; la normalisation ramène 1500.0 à 1500, et un normaliseur de champ propre aux dates les réécrit au format ISO avant la comparaison. L'équipe vérifie aussi la F1 sur les seuls noms : à 0,95 contre 0,70 pour la F1 complète, l'écart dit que l'agent choisit les bons outils mais se trompe d'arguments, le plus souvent en passant le montant toutes taxes comprises là où l'outil attend le montant hors taxes (point 6). La correction porte sur le schéma de l'outil, qui nomme désormais explicitement le champ `montant_ht`. L'assureur est supervisé par la CBUAE et le règlement reste validé par un gestionnaire. Les indicateurs suivis sont la F1 complète, la F1 sur les noms et leur écart.

### RH — le bon outil, le mauvais salaire

Un cabinet RH présent dans plusieurs émirats fait préparer par un agent les fins de contrat : appels attendus `verifier_contrat_mohre`, puis `calculer_fin_de_service` avec le salaire de base et l'ancienneté, conformément au décret-loi fédéral 33/2021 pour le secteur privé. L'agent appelle bien les deux outils, mais passe souvent le salaire total, allocations comprises, au lieu du salaire de base : l'appel faux est un FP, l'appel juste manquant un FN, et la F1 complète tombe à 0,5 sur ces scénarios alors que la F1 sur les noms reste à 1. Pour dix ans de service et un salaire de base de 10 000 AED, l'outil aurait calculé 85 000 AED ; avec un salaire total de 15 000 AED, il calcule 127 500 AED, une erreur que la seule lecture de la réponse finale aurait pu laisser passer. Le cabinet ajoute au schéma de l'outil un champ nommé `salaire_base_mensuel` et une description qui exclut les allocations. Les indicateurs suivis sont la F1 complète des parcours de fin de contrat et le nombre d'appels où le salaire passé ne correspond pas au salaire de base du contrat.

### Secteur public — un rendez-vous pris deux fois

Un service public en ligne accessible par UAE Pass laisse l'agent prendre des rendez-vous pour les usagers, en arabe ou en anglais. Après une mise à jour, des usagers reçoivent deux confirmations pour le même créneau : l'agent, après un délai de réponse de l'outil, a rappelé `prendre_rendez_vous` avec les mêmes arguments. L'ancienne évaluation, à base d'ensembles, donnait une F1 parfaite, parce que le doublon disparaissait ; avec un `Counter`, le scénario tombe à 2/3 et la régression apparaît (point 2). L'équipe corrige deux choses : l'outil reçoit une clé d'idempotence, comme à l'étape 12, et la barrière de déploiement refuse toute version dont un scénario contient un appel à effet répété. Les données des usagers sont soumises à la PDPL : les scénarios d'évaluation utilisent des identités fictives. Les indicateurs suivis sont la Tool Call F1 sur multi-ensembles et le nombre de rendez-vous en double par semaine.

## Pièges et limites

- **Comparer des ensembles.** Un appel répété disparaît ; pour un outil à effet, c'est précisément l'erreur à voir. On utilise `collections.Counter`.
- **Comparer des `str(dict)` ou des arguments bruts.** L'ordre des clés et l'écriture des valeurs créent de faux écarts ; on compare des clés JSON triées et normalisées.
- **Normaliser globalement.** Mettre tout en minuscules confond deux adresses Base58 ou deux références sensibles à la casse ; la normalisation se fait champ par champ.
- **Oublier l'ordre quand il compte.** La Tool Call F1 ne le voit pas ; on publie à côté une F1 ordonnée ou une exactitude de séquence pour les parcours où un contrôle doit précéder une action.
- **Mélanger l'abstention correcte et l'action non voulue.** « Rien d'attendu, rien appelé » est indéfini et se compte à part ; « rien d'attendu, un appel fait » vaut 0 et doit alerter.

### Exercice feuille blanche

1. Sans regarder le code, écrire `cle_appel` et `tool_call_f1` avec `Counter`, puis vérifier 0,8 sur l'exemple du point 7.
2. Prédire, puis vérifier : attendus [A, B, C], faits [A, A, B]. Que valent TP, FP, FN et la F1 avec `Counter`, puis avec `set` ? (Réponse : 2, 1, 1 et 4/6 ≈ 0,667 ; avec `set`, 2, 0, 1 et 4/5 = 0,8.)
3. Trouver le bug : dans `normaliser_valeur`, une chaîne est renvoyée par `s.lower()` quel que soit le champ. Quel appel faux peut alors être compté comme un vrai positif sur la plateforme crypto, et pourquoi la F1 monte-t-elle au lieu de baisser ?

## Pour aller plus loin

Quand un argument est un texte libre, comme le corps d'un e-mail, on le retire de la clé et on le fait juger séparément, par un juge LLM ou par une similarité sémantique, ce qui donne un crédit partiel par argument. Quand plusieurs plans sont valides, on écrit plusieurs suites de référence et l'on garde, pour chaque scénario, la meilleure F1. Enfin, les métriques d'ordre peuvent être plus fines que la sous-suite commune : distance d'édition entre suites d'appels, ou contraintes de précédence explicites (« `verifier_kyc` avant tout `initier_virement` ») vérifiées une par une sur la trace.

> Suite : [Agent Goal Accuracy](<60-Evaluation-Formule-Agent-Goal-Accuracy.md>) — étape 60.
