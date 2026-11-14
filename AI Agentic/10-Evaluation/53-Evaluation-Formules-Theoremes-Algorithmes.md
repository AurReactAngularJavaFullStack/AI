# Étape 53 — Évaluation — Formules, Théorèmes et Algorithmes

> Étape 53 du parcours · Prérequis : [Perplexité](<52-Perplexite-LLM.md>) · Suite : [Faithfulness](<54-Evaluation-Formule-Faithfulness.md>)

**Dossier :** 10-Evaluation  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers

**Leçon longue — les métriques qui évaluent un agent et son RAG, racontées puis démontrées**

## Introduction : pourquoi mesurer avec des formules précises

Tu as déjà construit un agent qui qualifie une demande, appelle des outils et laisse une trace (étapes 12 et 13), et tu as posé dès l'étape 13 bis le protocole qui le mesure : jeu d'évaluation, correcteurs, intervalle de Wilson, barrière d'intégration continue. En production, la question n'est plus « est-ce que ça marche sur mon poste ? » mais « est-ce que ça reste fiable après 10 000 requêtes, avec des clients qui reformulent en arabe puis en anglais, des documents réglementaires qui changent et des règles métier qui évoluent ? ». Les formules de ce chapitre donnent des chiffres que l'on peut mettre dans une pipeline d'intégration continue, exactement comme les tests d'intégration d'un projet Spring : Faithfulness, Answer Relevancy, précision et rappel, Context Precision, Tool Call F1.

Sans ces métriques, on se contente de « ça a l'air bien ». Avec elles, on peut écrire dans un ticket : « la Faithfulness est tombée de 0,92 à 0,71 après le dernier changement de prompt, la borne basse de Wilson passe sous le seuil, on bloque le déploiement ». Ce fichier est le récit du chapitre : il présente les cinq formules ensemble, montre comment elles se complètent et renvoie, pour chaque démonstration complète, au fichier qui la possède (étapes 50, 54, 55, 57 et 59).

## Définition

- **Faithfulness (fidélité)** : la part des affirmations de la réponse que le contexte récupéré justifie. Elle répond à « la réponse invente-t-elle des faits ? ». Détail à l'étape 54.
- **Answer Relevancy (pertinence de la réponse)** : la similarité moyenne entre la question posée et les questions qu'on peut reconstruire à partir de la réponse. Elle répond à « la réponse parle-t-elle de la question ? ». Détail à l'étape 55.
- **Précision, rappel, F1** : les trois taux de l'étape 50, appliqués aux décisions d'un composant (garder un document, appeler un outil).
- **Context Precision** : une précision pondérée par le rang ; elle répond à « le retriever a-t-il placé les bons morceaux en tête ? ». Son complément, **Context Recall**, répond à « a-t-il ramené tous les bons morceaux ? » (étapes 57 et 58).
- **Tool Call F1** : un F1 sur les **ensembles** d'appels d'outils (nom et arguments), qui ignore l'ordre. Il ne faut pas le confondre avec **ToolCallAccuracy** de RAGAS, qui compare la **séquence** des appels à la séquence de référence et tient compte de l'ordre (étape 59).
- **Agent Goal Accuracy** : le score binaire « l'objectif métier est-il atteint ? » (1 ou 0), moyenné sur les cas (étape 60).

## Rôle dans un agent

Toutes ces métriques servent au moment **observer** de la boucle percevoir → décider → agir → observer, hors ligne sur le jeu d'évaluation et en ligne sur un échantillon de conversations. Leur force est de se combiner : chacune regarde un maillon différent, et leur profil dit où chercher la panne.

| Symptôme | Maillon faible probable | Métrique qui le montre |
|---|---|---|
| Context Precision basse, Faithfulness haute | le retriever : la génération reste fidèle à de mauvais morceaux | Context Precision, Context Recall |
| Context Precision haute, Faithfulness basse | la génération : le modèle invente malgré de bons morceaux | Faithfulness |
| Faithfulness haute, Answer Relevancy basse | la réponse est fidèle, mais à côté de la question | Answer Relevancy |
| Tool Call F1 bas | le choix des outils ou de leurs arguments | Tool Call F1, précision ordonnée |
| tout est haut, mais la tâche n'aboutit pas | la tâche métier n'est pas finie | Agent Goal Accuracy |

## Équation complète

Faithfulness, avec S l'ensemble des affirmations de la réponse et V celles que le contexte justifie :

$$
\text{Faithfulness} = \frac{|V|}{|S|}
$$

Answer Relevancy, avec n questions régénérées :

$$
\text{Answer Relevancy} = \frac{1}{n} \sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{E_{g_i} \cdot E_o}{\lVert E_{g_i}\rVert \, \lVert E_o\rVert}
$$

Précision, rappel et F1 (étape 50) :

$$
\text{Préc} = \frac{TP}{TP + FP}, \qquad \text{Rap} = \frac{TP}{TP + FN}, \qquad F_1 = \frac{2\,TP}{2\,TP + FP + FN}
$$

Context Precision sur K morceaux classés, avec vₖ = 1 si le morceau de rang k est pertinent :

$$
\text{Context Precision} = \frac{\sum_{k=1}^{K} \text{Precision@}k \cdot v_k}{\sum_{k=1}^{K} v_k}
\qquad
\text{Precision@}k = \frac{1}{k}\sum_{j=1}^{k} v_j
$$

Tool Call F1, sur les multiensembles A (appels attendus) et R (appels réels) :

$$
TP = |A \cap R|, \qquad FP = |R| - TP, \qquad FN = |A| - TP, \qquad \text{Tool Call } F_1 = \frac{2\,TP}{2\,TP + FP + FN}
$$

Variante ordonnée, dans l'esprit de ToolCallAccuracy, où aᵢ et rᵢ sont les appels à la position i :

$$
\text{Préc}_{\text{ord}} = \frac{\#\{\,i : a_i = r_i\,\}}{\max(|A|, |R|)}
$$

## Décryptage des symboles

$$
S,\; V
$$

**Sens :** S est l'ensemble des affirmations atomiques extraites de la réponse ; V ⊆ S est le sous-ensemble que le juge déclare déductible du contexte · **Type / plage :** ensembles finis, |V| ≤ |S| · **Variable Python :** la liste `verdicts`, un booléen par affirmation.

$$
E_o,\; E_{g_i}
$$

**Sens :** embedding de la question d'origine, et embedding de la i-ème question régénérée à partir de la réponse · **Type / plage :** vecteurs de même dimension, non nuls · **Variable Python :** `e_o`, et les éléments de `generees`.

$$
n
$$

**Sens :** nombre de questions régénérées (souvent 3 à 5) · **Type / plage :** entier ≥ 1 · **Variable Python :** `len(generees)`.

$$
v_k
$$

**Sens :** pertinence du morceau classé au rang k (1 pertinent, 0 non) · **Type / plage :** 0 ou 1 · **Variable Python :** les éléments de `pertinence`.

$$
K
$$

**Sens :** nombre de morceaux récupérés et injectés dans le contexte · **Type / plage :** entier ≥ 0 · **Variable Python :** `len(pertinence)`.

$$
A,\; R
$$

**Sens :** appels d'outils attendus et appels réellement faits ; un appel est un couple (nom, arguments) · **Type / plage :** multiensembles : un même appel peut compter deux fois · **Variable Python :** `attendus`, `reels`, convertis en `Counter` par `cle_appel`.

$$
\varepsilon
$$

**Sens :** taux d'erreur du juge, probabilité qu'il inverse un verdict · **Type / plage :** réel dans [0 ; 0,5[ · **Variable Python :** `taux_erreur` dans `JugeBruite`.

## Démonstration

### 1. Faithfulness est un nombre entre 0 et 1, indéfini sans affirmation

Comme V est inclus dans S, 0 ≤ |V| ≤ |S|. Si |S| > 0, on divise par |S| et 0 ≤ |V|/|S| ≤ 1. Le score vaut 1 si et seulement si chaque affirmation est justifiée, 0 si et seulement si aucune ne l'est. Si |S| = 0, la réponse n'affirme rien (« je ne sais pas ») : le score n'existe pas, et le programme renvoie `None`. L'étape 54 démontre la monotonie, la différence entre moyenne des ratios et ratio des sommes, et le danger du NaN dans une barrière.

**Exemple.** Contexte récupéré : « Pour un choc sur parking, le plafond de garantie dommages matériels est de 5 000 AED. La franchise standard est de 500 AED. Aucune franchise ne s'applique si le véhicule est stationné et que le conducteur est absent. » Réponse : « Le plafond est de 5 000 AED et la franchise est de 1 000 AED. Aucune franchise ne s'applique. » Trois affirmations : le plafond est justifié ; la franchise de 1 000 AED est inventée ; « aucune franchise » oublie la condition du contexte et n'est pas déductible telle quelle. Faithfulness = 1/3 ≈ 0,333.

### 2. Answer Relevancy, calculée à la main

Embeddings simplifiés en deux dimensions : Eₒ = (0,9 ; 0,1), puis trois questions régénérées g₁ = (0,85 ; 0,15), g₂ = (0,7 ; 0,4) et g₃ = (0,2 ; 0,8). Les normes valent ‖Eₒ‖ = √0,82 = 0,90554, ‖g₁‖ = √0,745 = 0,86313, ‖g₂‖ = √0,65 = 0,80623 et ‖g₃‖ = √0,68 = 0,82462.

$$
\cos(g_1, E_o) = \frac{0{,}9 \times 0{,}85 + 0{,}1 \times 0{,}15}{0{,}90554 \times 0{,}86313} = \frac{0{,}78}{0{,}78160} = 0{,}998
$$

$$
\cos(g_2, E_o) = \frac{0{,}63 + 0{,}04}{0{,}90554 \times 0{,}80623} = \frac{0{,}67}{0{,}73007} = 0{,}918
$$

$$
\cos(g_3, E_o) = \frac{0{,}18 + 0{,}08}{0{,}90554 \times 0{,}82462} = \frac{0{,}26}{0{,}74673} = 0{,}348
$$

La moyenne vaut (0,998 + 0,918 + 0,348)/3 = 0,755. L'ancienne version de ce calcul écrivait 0,999, 0,89, 0,34 et une moyenne de 0,743 : les arrondis intermédiaires étaient faux. Chaque cosinus est entre −1 et 1 par l'inégalité de Cauchy-Schwarz (étape 14), donc la moyenne aussi. L'étape 55 montre que ce score est le produit scalaire de ê_o avec le centroïde des questions normalisées, et pourquoi une réponse évasive doit recevoir 0.

### 3. Précision, rappel et F1 sur des appels d'outils

Appels attendus : `rechercher_politique(pays="AE", theme="periode_essai")` puis `verifier_eligibilite()`. Appels réels : les deux mêmes, plus `rechercher_politique(pays="IN", theme="periode_essai")`, un appel sur le mauvais pays. TP = 2, FP = 1, FN = 0, donc précision 2/3 = 0,667, rappel 2/2 = 1 et F1 = 4/5 = 0,8. La forme en comptes 2TP/(2TP + FP + FN), son encadrement entre min(Préc, Rap) et la moyenne arithmétique, et le Fβ sont démontrés à l'étape 50.

### 4. Context Precision : une précision pondérée par le rang

La formule ne fait la moyenne des Precision@k qu'aux rangs où le morceau est pertinent. Pour v = (1, 0, 1) : au rang 1, Precision@1 = 1 ; au rang 3, Precision@3 = 2/3. Context Precision = (1 + 2/3)/2 = 0,8333. Pour v = (0, 1, 1), les mêmes deux morceaux pertinents sont arrivés plus tard : (1/2 + 2/3)/2 = 0,5833.

**Bornes et cas d'égalité.** Chaque Precision@k est une part de morceaux pertinents, donc entre 0 et 1 ; une moyenne de nombres entre 0 et 1 reste entre 0 et 1. Elle vaut 1 si et seulement si chaque Precision@k compté vaut 1, c'est-à-dire si aucun morceau non pertinent ne précède un morceau pertinent : tous les pertinents sont en tête. C'est le cas de (1, 1, 0).

**Le dénominateur nul.** Si aucun morceau n'est pertinent, la somme des vₖ vaut 0. RAGAS renvoie alors 0, ce qui est cohérent : le retriever a ramené K morceaux et aucun ne sert, c'est un échec, pas une absence de mesure. Si K = 0, il n'y a rien à juger, et le programme renvoie `None`. Le score ne pénalise pas les morceaux pertinents jamais ramenés : c'est le rôle du Context Recall (étape 58). L'étape 57 démontre qu'avancer un morceau pertinent augmente le score.

### 5. Tool Call F1 ignore l'ordre, la variante ordonnée non

Le F1 compare des multiensembles : l'ordre des éléments n'y existe pas. Si l'agent appelle `verifier_eligibilite()` avant `rechercher_politique(...)`, A ∩ R contient toujours les deux appels, TP = 2, FP = FN = 0 et le Tool Call F1 vaut 1. La variante ordonnée compare position par position : aucune position ne coïncide, elle vaut 0. Laquelle choisir dépend du métier : si la vérification d'éligibilité n'a de sens qu'après la lecture de la politique, l'ordre compte et le F1 seul ne suffit pas.

**Pourquoi un multiensemble et pas un ensemble.** Si l'agent appelle deux fois `rechercher_politique(pays="AE", ...)` et jamais `verifier_eligibilite()`, un ensemble ne verrait qu'un appel juste et aucun appel en trop : précision 1, rappel 1/2, F1 0,667. Le multiensemble compte le doublon comme un faux positif : TP = 1, FP = 1, FN = 1, F1 = 2/4 = 0,5. Un appel répété coûte des tokens et parfois une action : il doit se voir.

**Pourquoi des clés triées.** Un dictionnaire Python n'est pas hachable, et `{"pays": "AE", "theme": …}` et `{"theme": …, "pays": "AE"}` sont le même appel. On sérialise donc les arguments avec `json.dumps(..., sort_keys=True)` : les deux écritures donnent la même chaîne.

### 6. Un juge LLM n'est pas déterministe, et son bruit biaise le score

L'ancienne version affirmait que ces algorithmes « sont déterministes une fois le juge fixé ». C'est faux : un LLM échantillonne ses tokens, et même à température 0, une API peut renvoyer des sorties différentes d'un appel à l'autre. On modélise un juge qui inverse chaque verdict avec une probabilité ε, indépendamment d'une affirmation à l'autre. Le score mesuré F̂ est la moyenne de |S| variables Xⱼ qui valent 1 si le juge dit « supportée ». Pour une affirmation vraiment supportée, P(Xⱼ = 1) = 1 − ε ; pour une affirmation non supportée, P(Xⱼ = 1) = ε. Par linéarité de l'espérance, avec F = |V|/|S| la vraie fidélité :

$$
E[\hat F] = F(1 - \varepsilon) + (1 - F)\,\varepsilon = \varepsilon + (1 - 2\varepsilon)\,F
$$

Le score attendu est tiré vers 0,5 : avec F = 0,75 et ε = 0,1, il vaut 0,70. Chaque Xⱼ a une variance ε(1 − ε), dans les deux cas, et les Xⱼ sont indépendants, donc

$$
\text{Var}(\hat F) = \frac{\varepsilon(1-\varepsilon)}{|S|}
$$

soit un écart-type de √(0,09/20) = 0,067 pour 20 affirmations. Le programme fait passer cinq fois un tel juge sur 20 affirmations dont 15 sont supportées : il obtient 0,65, 0,65, 0,65, 0,70 et 0,75, de moyenne 0,68 et d'écart-type 0,045. Conséquences pratiques : fixer la version exacte du modèle juge, sa température et son prompt ; répéter chaque mesure trois à cinq fois ; publier la moyenne **et** la dispersion ; calibrer le juge contre des annotations humaines (étape 13 bis) pour estimer ε. Une baisse de 0,75 à 0,70 entre deux versions peut n'être que du bruit.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| \|V\| / \|S\| | `faithfulness(verdicts)` |
| cos(E_gᵢ, Eₒ) | `cosinus(g, e_o)` (fonction canonique du parcours) |
| Answer Relevancy | `answer_relevancy(e_o, generees)` |
| Préc, Rap, F1 | `precision_rappel_f1(tp, fp, fn)` |
| vₖ, Context Precision | `pertinence`, `context_precision(pertinence)` |
| un appel (nom, arguments) | `cle_appel(appel)` |
| Tool Call F1 | `tool_call_f1(attendus, reels)` |
| Préc_ord | `precision_ordonnee(attendus, reels)` |
| juge de taux d'erreur ε | `JugeBruite(verite, taux_erreur, graine)` |

### Déroulé, ligne par ligne

**`faithfulness(verdicts)`** reçoit un booléen par affirmation, tel que le juge l'a rendu. `if not verdicts: return None` traite la réponse qui n'affirme rien : on ne divise pas par zéro et on ne fabrique pas un NaN. Ensuite, `sum(1 for v in verdicts if v)` compte |V| et la division par `len(verdicts)` donne |V|/|S| : 1/3 sur l'exemple de la franchise.

**`cosinus(a, b)`** est la fonction canonique du parcours : elle refuse deux dimensions différentes, calcule les deux normes, lève `ValueError` si l'une est nulle, puis renvoie le produit scalaire divisé par le produit des normes, ramené dans [−1, 1] pour absorber un arrondi. **`answer_relevancy(e_o, generees)`** renvoie `None` s'il n'y a aucune question régénérée, puis la moyenne des cosinus : 0,998, 0,918 et 0,348 donnent 0,755.

**`precision_rappel_f1(tp, fp, fn)`** calcule les trois taux, chacun à `None` si son dénominateur est nul. Le F1 utilise la forme en comptes, qui reste définie quand la précision ne l'est pas. Avec (2, 1, 0), elle renvoie 0,667, 1,0 et 0,8.

**`context_precision(pertinence)`**.

- `if not pertinence: return None` : sans morceau, rien à juger.
- La garde sur `v not in (0, 1)` refuse une note graduée, que cette formule ne sait pas traiter.
- `if sum(pertinence) == 0: return 0.0` : la convention RAGAS, un échec du retriever.
- La boucle tient `vus`, le nombre de pertinents vus jusqu'au rang `k`. À chaque rang pertinent, elle ajoute `vus / k`, qui est Precision@k. Pour (1, 0, 1) : rang 1, `vus = 1`, on ajoute 1 ; rang 2, non pertinent, rien ; rang 3, `vus = 2`, on ajoute 2/3. La somme 5/3 est divisée par 2 : 0,8333.

**`cle_appel(appel)`** renvoie le couple `(nom, json.dumps(args, sort_keys=True, ensure_ascii=False))`. Le tri des clés rend les deux écritures de `rechercher_politique` identiques ; `ensure_ascii=False` garde lisibles les arguments en arabe.

**`tool_call_f1(attendus, reels)`** transforme chaque liste en `Counter` de clés. L'opérateur `&` garde, pour chaque clé, le minimum des deux comptes : c'est l'intersection des multiensembles. `tp` en est la taille, `len(reels) - tp` les appels en trop, `len(attendus) - tp` les appels manquants, puis la forme en comptes du F1. Rien attendu et rien appelé donne `None`.

**`precision_ordonnee(attendus, reels)`** compare position par position avec `zip` et divise par la plus longue des deux listes, pour qu'un appel manquant ou en trop compte comme une position ratée.

**`JugeBruite`** garde la vérité et un générateur `random.Random(graine)` qui lui est propre, pour que chaque passage soit reproductible. `juger()` renvoie chaque verdict tel quel si le tirage dépasse `taux_erreur`, inversé sinon.

**`main()`**, bloc par bloc.

1. Faithfulness de la réponse sur la franchise (1/3), puis `None` pour une réponse sans affirmation.
2. Les trois cosinus et leur moyenne, comparés aux valeurs calculées à la main ; puis `None` sans question et `ValueError` sur un vecteur nul.
3. Les trois taux pour TP = 2, FP = 1, FN = 0.
4. Cinq listes de pertinence : 0,8333, 0,5833, 1, 0 et `None`.
5. Trois scénarios d'appels : un appel en trop (F1 0,8, ordonnée 0,333), l'ordre inversé (F1 1, ordonnée 0), le même appel deux fois (F1 0,5). Le premier scénario utilise l'écriture des arguments dans l'autre ordre : il compte quand même comme juste.
6. Cinq passages d'un juge à 10 % d'erreur, avec les graines 1 à 5 : les scores diffèrent, leur écart-type est positif. Le même protocole avec un juge sans erreur donne cinq fois 0,75.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`answer_relevancy(e_o, generees)`** — Cette fonction joue le rôle d'un examinateur qui, pour savoir si une réponse colle à la question, demande à plusieurs témoins de deviner la question rien qu'en lisant la réponse : elle reçoit le vecteur de la question d'origine et la liste des vecteurs des questions régénérées, renvoie `None` s'il n'y en a aucune, et sinon calcule le cosinus de chacune avec la question d'origine grâce à `cosinus`, puis renvoie leur moyenne. Sur l'exemple, les trois cosinus 0,998, 0,918 et 0,348 donnent 0,755 ; un vecteur nul, lui, fait lever `ValueError` par `cosinus`, ce que `main` vérifie.

**`precision_rappel_f1(tp, fp, fn)`** — Celle-ci est le comptable qui tire trois ratios d'un même livre de comptes : elle reçoit les vrais positifs, les faux positifs et les faux négatifs, calcule la précision TP ÷ (TP + FP) et le rappel TP ÷ (TP + FN), chacun remplacé par `None` si son dénominateur est nul, puis le F1 sous sa forme en comptes, 2TP ÷ (2TP + FP + FN), qui reste défini même quand la précision ne l'est pas. Elle renvoie le triplet (précision, rappel, F1) : 0,667, 1,0 et 0,8 pour deux appels justes et un appel en trop, et c'est elle qui fournit le F1 final à `tool_call_f1`.

**`context_precision(pertinence)`** — Cette fonction est le bibliothécaire qui juge un rayonnage dans l'ordre où il le présente au lecteur : elle reçoit la liste des pertinences des morceaux retrouvés, rang par rang, renvoie `None` si la liste est vide, lève `ValueError` pour une note autre que 0 ou 1, et renvoie 0 si aucun morceau n'est pertinent, selon la convention RAGAS. Sinon, elle avance rang après rang en comptant les pertinents déjà vus, ajoute la Precision@k à chaque rang pertinent et divise la somme par le nombre de pertinents : (1, 0, 1) donne 0,8333, (0, 1, 1) donne 0,5833 et (1, 1, 0) donne 1, ce qui récompense le retriever qui place les bons morceaux en tête.

**`cle_appel(appel)`** — Celle-ci est le notaire qui recopie chaque appel d'outil dans une forme officielle, pour qu'on puisse comparer deux actes sans se laisser tromper par la mise en page : elle reçoit un dictionnaire avec le nom de l'outil et ses arguments, et renvoie le couple formé du nom et des arguments sérialisés en JSON avec les clés triées et les caractères non ASCII conservés. Un dictionnaire n'étant pas hachable, cette clé permet de ranger les appels dans un `Counter` ; grâce au tri, les deux écritures de `rechercher_politique`, avec `pays` puis `theme` ou l'inverse, deviennent identiques et comptent comme un même appel juste.

**`precision_ordonnee(attendus, reels)`** — Cette fonction est l'arbitre pointilleux qui exige que chaque geste vienne à son tour : elle reçoit la liste des appels attendus et celle des appels réellement faits, renvoie `None` si les deux sont vides, puis compare position par position, avec `cle_appel`, les appels alignés par `zip`, et divise le nombre de positions justes par la longueur de la plus longue des deux listes, pour qu'un appel manquant ou en trop compte comme une position ratée. Elle renvoie 0,333 pour le scénario à un appel en trop, 0 pour l'ordre inversé alors que le F1 vaut 1, et 0,5 pour le même appel répété deux fois.

**`JugeBruite.__init__(verite, taux_erreur, graine)`** — Le constructeur installe un juge LLM simulé à sa table, avec son dossier et son propre tempérament : il reçoit la liste des vrais verdicts, une probabilité d'erreur et une graine, garde les deux premiers et crée un générateur `random.Random(graine)` qui n'appartient qu'à ce juge, pour que chaque passage soit reproductible sans dépendre du hasard global. Il ne renvoie rien ; `main` fabrique cinq juges à 10 % d'erreur avec les graines 1 à 5, puis cinq juges sans erreur, sur 20 affirmations dont 15 sont vraiment supportées.

**`JugeBruite.juger()`** — Cette méthode est le moment où le juge rend sa copie, avec ses distractions : pour chaque verdict vrai du dossier, elle tire un nombre au hasard avec le générateur du juge, recopie le verdict tel quel si ce nombre atteint ou dépasse le taux d'erreur, et l'inverse sinon. Elle renvoie la liste des verdicts ainsi bruités, que `faithfulness` transforme en score : avec 10 % d'erreur, les cinq passages donnent 0,65, 0,65, 0,65, 0,7 et 0,75, de moyenne 0,680 et d'écart-type 0,045, alors que la vraie valeur est 0,75, ce qui montre qu'un juge échantillonné n'est pas déterministe.

**`main()`** — C'est le chef d'orchestre des six démonstrations : il calcule la fidélité 1/3 de la réponse sur la franchise et le `None` d'une réponse sans affirmation, les trois cosinus et leur moyenne 0,755 avec les deux cas limites, puis les taux 0,667, 1,0 et 0,8 pour TP = 2, FP = 1, FN = 0. Il passe ensuite cinq listes de pertinence à `context_precision`, oppose le Tool Call F1, qui ignore l'ordre, à la précision ordonnée sur trois scénarios d'appels, et fait enfin juger 20 affirmations par cinq juges bruités puis cinq juges exacts, qui doivent tous rendre 0,75 ; « OK » n'apparaît que si chaque `assert` est passé.

```python
"""Étape 53 — les cinq formules d'évaluation en bibliothèque standard, et un juge qui n'est pas déterministe."""
import json
import math
import random
import statistics
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- 1. Faithfulness
def faithfulness(verdicts: list[bool]) -> float | None:
    """|V| / |S| : part des affirmations jugées supportées. None si la réponse n'affirme rien."""
    if not verdicts:
        return None
    return sum(1 for v in verdicts if v) / len(verdicts)


# ---------------------------------------------------------------- 2. Answer Relevancy
def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


def answer_relevancy(e_o: list[float], generees: list[list[float]]) -> float | None:
    """Moyenne des cosinus entre la question d'origine et les n questions régénérées. None si n = 0."""
    if not generees:
        return None
    return sum(cosinus(g, e_o) for g in generees) / len(generees)


# ---------------------------------------------------------------- 3. Précision, rappel, F1
def precision_rappel_f1(tp: int, fp: int, fn: int) -> tuple[float | None, float | None, float | None]:
    p = None if tp + fp == 0 else tp / (tp + fp)
    r = None if tp + fn == 0 else tp / (tp + fn)
    f1 = None if 2 * tp + fp + fn == 0 else 2 * tp / (2 * tp + fp + fn)   # forme en comptes (étape 50)
    return p, r, f1


# ---------------------------------------------------------------- 4. Context Precision
def context_precision(pertinence: list[int]) -> float | None:
    """Σ_k Precision@k · v_k / Σ_k v_k. None si aucun chunk ; 0 si aucun n'est pertinent (convention RAGAS)."""
    if not pertinence:
        return None
    if any(v not in (0, 1) for v in pertinence):
        raise ValueError("v_k vaut 0 ou 1")
    if sum(pertinence) == 0:
        return 0.0
    somme, vus = 0.0, 0
    for k, v in enumerate(pertinence, start=1):
        vus += v
        if v:
            somme += vus / k            # Precision@k, comptée seulement aux rangs pertinents
    return somme / sum(pertinence)


# ---------------------------------------------------------------- 5. Tool Call F1 et variante ordonnée
def cle_appel(appel: dict) -> tuple[str, str]:
    """Un dict n'est pas hachable : on le sérialise avec des clés triées, pour que l'ordre des arguments ne compte pas."""
    return appel["nom"], json.dumps(appel["args"], sort_keys=True, ensure_ascii=False)


def tool_call_f1(attendus: list[dict], reels: list[dict]) -> float | None:
    """F1 sur les multiensembles d'appels (nom + arguments) : l'ordre ne compte pas, les répétitions si."""
    a = Counter(cle_appel(x) for x in attendus)
    r = Counter(cle_appel(x) for x in reels)
    tp = sum((a & r).values())
    return precision_rappel_f1(tp, len(reels) - tp, len(attendus) - tp)[2]


def precision_ordonnee(attendus: list[dict], reels: list[dict]) -> float | None:
    """Variante sensible à l'ordre (esprit de ToolCallAccuracy) : position par position."""
    if not attendus and not reels:
        return None
    justes = sum(1 for x, y in zip(attendus, reels) if cle_appel(x) == cle_appel(y))
    return justes / max(len(attendus), len(reels))


# ---------------------------------------------------------------- juge simulé
class JugeBruite:
    """Simule un juge LLM échantillonné : il inverse chaque verdict avec la probabilité taux_erreur."""

    def __init__(self, verite: list[bool], taux_erreur: float, graine: int):
        self.verite = verite
        self.taux_erreur = taux_erreur
        self.rng = random.Random(graine)

    def juger(self) -> list[bool]:
        return [v if self.rng.random() >= self.taux_erreur else not v for v in self.verite]


def main() -> None:
    print("1. Faithfulness : plafond juste, franchise inventée, exclusion déformée")
    f = faithfulness([True, False, False])
    print(f"  |V| / |S| = 1/3 = {f:.3f}   ;   réponse sans affirmation : {faithfulness([])}")
    assert abs(f - 1 / 3) < 1e-12 and faithfulness([]) is None

    print("2. Answer Relevancy : trois questions régénérées")
    e_o = [0.9, 0.1]
    generees = [[0.85, 0.15], [0.7, 0.4], [0.2, 0.8]]
    cos = [cosinus(g, e_o) for g in generees]
    ar = answer_relevancy(e_o, generees)
    print(f"  cosinus = {[round(c, 3) for c in cos]}   moyenne = {ar:.3f}")
    assert [round(c, 3) for c in cos] == [0.998, 0.918, 0.348] and round(ar, 3) == 0.755
    assert answer_relevancy(e_o, []) is None
    try:
        answer_relevancy(e_o, [[0.0, 0.0]])
    except ValueError:
        print("  vecteur nul → ValueError ; aucune question → None")
    else:
        raise AssertionError("un vecteur nul aurait dû être refusé")

    print("3. Précision, rappel, F1 sur des appels d'outils")
    p, r, f1 = precision_rappel_f1(2, 1, 0)
    print(f"  TP = 2, FP = 1, FN = 0 : précision = {p:.3f}  rappel = {r:.1f}  F1 = {f1:.1f}")
    assert (round(p, 3), r, round(f1, 3)) == (0.667, 1.0, 0.8)

    print("4. Context Precision, pondérée par le rang")
    for v in ([1, 0, 1], [0, 1, 1], [1, 1, 0], [0, 0, 0], []):
        cp = context_precision(v)
        print(f"  {str(v):9s} → {cp if cp is None else round(cp, 4)}")
    assert round(context_precision([1, 0, 1]), 4) == 0.8333 and round(context_precision([0, 1, 1]), 4) == 0.5833
    assert context_precision([1, 1, 0]) == 1.0 and context_precision([0, 0, 0]) == 0.0
    assert context_precision([]) is None

    print("5. Tool Call F1 (ordre ignoré) contre précision ordonnée")
    politique_ae = {"nom": "rechercher_politique", "args": {"pays": "AE", "theme": "periode_essai"}}
    politique_ae_bis = {"nom": "rechercher_politique", "args": {"theme": "periode_essai", "pays": "AE"}}
    politique_in = {"nom": "rechercher_politique", "args": {"pays": "IN", "theme": "periode_essai"}}
    eligibilite = {"nom": "verifier_eligibilite", "args": {}}
    attendus = [politique_ae, eligibilite]
    cas = {"un appel en trop": [politique_ae_bis, politique_in, eligibilite],
           "ordre inversé": [eligibilite, politique_ae],
           "même appel deux fois": [politique_ae, politique_ae]}
    for nom, reels in cas.items():
        print(f"  {nom:21s} F1 = {tool_call_f1(attendus, reels):.3f}   ordonnée = {precision_ordonnee(attendus, reels):.3f}")
    assert tool_call_f1(attendus, cas["un appel en trop"]) == 0.8
    assert tool_call_f1(attendus, cas["ordre inversé"]) == 1.0 and precision_ordonnee(attendus, cas["ordre inversé"]) == 0.0
    assert tool_call_f1(attendus, cas["même appel deux fois"]) == 0.5      # le Counter compte les répétitions
    assert tool_call_f1([], []) is None

    print("6. Un juge LLM n'est pas déterministe : 20 affirmations, 15 vraiment supportées")
    verite = [True] * 15 + [False] * 5
    scores = [faithfulness(JugeBruite(verite, 0.10, graine).juger()) for graine in range(1, 6)]
    print(f"  5 passages du juge : {scores}")
    print(f"  moyenne = {statistics.mean(scores):.3f}   écart-type = {statistics.stdev(scores):.3f}   vraie valeur = 0.750")
    assert statistics.stdev(scores) > 0 and len(set(scores)) > 1
    exacts = [faithfulness(JugeBruite(verite, 0.0, graine).juger()) for graine in range(1, 6)]
    assert exacts == [0.75] * 5
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Faithfulness : plafond juste, franchise inventée, exclusion déformée
  |V| / |S| = 1/3 = 0.333   ;   réponse sans affirmation : None
2. Answer Relevancy : trois questions régénérées
  cosinus = [0.998, 0.918, 0.348]   moyenne = 0.755
  vecteur nul → ValueError ; aucune question → None
3. Précision, rappel, F1 sur des appels d'outils
  TP = 2, FP = 1, FN = 0 : précision = 0.667  rappel = 1.0  F1 = 0.8
4. Context Precision, pondérée par le rang
  [1, 0, 1] → 0.8333
  [0, 1, 1] → 0.5833
…
5. Tool Call F1 (ordre ignoré) contre précision ordonnée
  un appel en trop      F1 = 0.800   ordonnée = 0.333
  ordre inversé         F1 = 1.000   ordonnée = 0.000
  même appel deux fois  F1 = 0.500   ordonnée = 0.500
6. Un juge LLM n'est pas déterministe : 20 affirmations, 15 vraiment supportées
  5 passages du juge : [0.65, 0.65, 0.65, 0.7, 0.75]
  moyenne = 0.680   écart-type = 0.045   vraie valeur = 0.750
OK — toutes les vérifications sont passées.
```

### La même formule côté Java

Dans un service Spring, la même fonction s'écrit en renvoyant un `OptionalDouble` vide plutôt qu'un `Double.NaN` : un NaN passe silencieusement les comparaisons d'une barrière de qualité (étape 54), un `Optional` vide oblige l'appelant à traiter le cas.

```java
import java.util.List;
import java.util.OptionalDouble;
import java.util.function.Predicate;

public OptionalDouble faithfulness(List<String> claims, Predicate<String> estSupportee) {
    if (claims.isEmpty()) {
        return OptionalDouble.empty();          // indéfini : la réponse n'affirme rien
    }
    long supportees = claims.stream().filter(estSupportee).count();
    return OptionalDouble.of((double) supportees / claims.size());
}
```

Le prédicat `estSupportee` encapsule l'appel au juge LLM : c'est un port, au sens de l'architecture hexagonale, que l'on remplace par un faux juge dans les tests.

## Squelette algorithmique

Le chapitre repose sur quatre algorithmes. Faithfulness et Answer Relevancy appellent un LLM : leur coût réel est le nombre d'appels au modèle, pas les opérations Python. Context Precision et Tool Call F1 sont des calculs exacts sur des listes, sans modèle.

### Faithfulness : extraire, juger, compter

Entrées : la question, le contexte récupéré, la réponse. Sortie : un score dans [0, 1], ou « indéfini » si la réponse n'affirme rien, plus la liste des affirmations non justifiées. L'idée : découper la réponse en affirmations atomiques, faire juger chacune contre le contexte, compter.

```text
ALGORITHME Faithfulness
ENTRÉES : question, contexte, réponse, juge
SORTIE : score ∈ [0, 1] ou INDÉFINI, liste des affirmations rejetées
  S ← juge.extraire_affirmations(réponse)          (un appel au LLM)
  SI |S| = 0 ALORS
    RETOURNER INDÉFINI, []
  FIN SI
  nb_supportées ← 0 ; rejetées ← []
  POUR chaque affirmation s de S FAIRE
    SI juge.est_déductible(s, contexte) ALORS        (un appel au LLM, ou un lot)
      nb_supportées ← nb_supportées + 1
    SINON
      ajouter s à rejetées                             (à journaliser pour l'analyse humaine)
    FIN SI
  FIN POUR
  RETOURNER nb_supportées / |S|, rejetées
```

**Complexité :** 1 + |S| appels au juge si l'on juge une affirmation par appel, ou 2 appels si l'on juge toutes les affirmations en un lot ; c'est ce terme, en latence et en tokens, qui domine. Le comptage lui-même est en O(|S|) en temps, et la mémoire en O(|S|) pour garder la liste des affirmations et des rejets.

**Du squelette au code :** l'extraction et le jugement sont faits par le LLM ; le programme reçoit leur résultat sous la forme de la liste `verdicts`. Le test `|S| = 0` est le `if not verdicts: return None` de `faithfulness`, et la boucle de comptage est la somme `sum(1 for v in verdicts if v)` divisée par `len(verdicts)`. `JugeBruite.juger` joue le rôle de `juge.est_déductible` sur toutes les affirmations d'un coup.

### Answer Relevancy : régénérer, encoder, moyenner

Entrées : la question d'origine, la réponse, un nombre n de questions à régénérer. Sortie : un score dans [−1, 1], en pratique dans [0, 1]. L'idée : si la réponse répond vraiment à la question, les questions qu'on peut reconstruire à partir d'elle ressemblent à la question posée.

```text
ALGORITHME AnswerRelevancy
ENTRÉES : question, réponse, n, modèle d'embedding
SORTIE : score ou INDÉFINI
  questions ← LLM.générer_questions(réponse, n)
  SI questions est vide ALORS
    RETOURNER INDÉFINI
  FIN SI
  e_o ← embedding(question)
  somme ← 0
  POUR chaque question q de questions FAIRE
    e_g ← embedding(q)                              (même modèle que pour e_o)
    SI ‖e_g‖ = 0 OU ‖e_o‖ = 0 ALORS
      ERREUR « vecteur nul : cosinus non défini »
    FIN SI
    somme ← somme + (e_g · e_o) / (‖e_g‖ ‖e_o‖)
  FIN POUR
  RETOURNER somme / |questions|
```

**Complexité :** un appel au LLM pour régénérer les n questions et n + 1 appels au modèle d'embedding (ou un seul en lot) dominent le coût. Le calcul des n cosinus en dimension d coûte O(n·d) en temps, parce que chaque produit scalaire et chaque norme parcourt les d coordonnées une fois ; la mémoire supplémentaire est en O(d) pour un vecteur à la fois, ou O(n·d) si l'on garde tous les embeddings.

**Du squelette au code :** les embeddings arrivent déjà calculés dans `e_o` et `generees`. Le test « questions vide » est le `if not generees: return None` de `answer_relevancy` ; le contrôle de norme nulle et le calcul du cosinus sont dans `cosinus` ; la somme et la division sont la ligne `sum(cosinus(g, e_o) for g in generees) / len(generees)`.

### Context Precision : un seul passage sur le classement

Entrées : la liste des pertinences v₁ … v_K, dans l'ordre du classement. Sortie : un score dans [0, 1], 0 si aucun morceau n'est pertinent, indéfini si K = 0. L'idée : tenir le nombre de pertinents déjà vus pour obtenir Precision@k sans recompter.

```text
ALGORITHME ContextPrecision
ENTRÉES : v[1..K], chaque v[k] ∈ {0, 1}
SORTIE : score ∈ [0, 1] ou INDÉFINI
  SI K = 0 ALORS
    RETOURNER INDÉFINI
  FIN SI
  R ← Σ v[k]
  SI R = 0 ALORS
    RETOURNER 0                                       (convention RAGAS : échec du retriever)
  FIN SI
  vus ← 0 ; somme ← 0
  POUR k DE 1 À K FAIRE
    vus ← vus + v[k]
    SI v[k] = 1 ALORS
      somme ← somme + vus / k                         (Precision@k)
    FIN SI
  FIN POUR
  RETOURNER somme / R
```

**Complexité :** O(K) en temps, parce que la somme R et la boucle parcourent chacune la liste une fois et que Precision@k s'obtient en O(1) grâce au compteur `vus` ; recalculer Precision@k depuis le début à chaque rang coûterait O(K²). La mémoire supplémentaire est en O(1) : trois nombres.

**Du squelette au code :** les deux tests de début sont les deux premiers `return` de `context_precision` ; R est `sum(pertinence)` ; la boucle `POUR` est la boucle `for k, v in enumerate(pertinence, start=1)`, et la ligne `somme ← somme + vus / k` est `somme += vus / k`.

### Tool Call F1 : normaliser, compter, intersecter

Entrées : la liste A des appels attendus et la liste R des appels réels, chacun avec un nom et un dictionnaire d'arguments. Sortie : un F1 dans [0, 1], ou indéfini si les deux listes sont vides. L'idée : transformer chaque appel en une clé comparable, puis compter les clés comme un multiensemble.

```text
ALGORITHME ToolCallF1
ENTRÉES : A (appels attendus), R (appels réels)
SORTIE : F1 ∈ [0, 1] ou INDÉFINI
  SI |A| = 0 ET |R| = 0 ALORS
    RETOURNER INDÉFINI
  FIN SI
  compte_A ← multiensemble vide ; compte_R ← multiensemble vide
  POUR chaque appel x de A FAIRE
    compte_A[(x.nom, sérialiser_trié(x.arguments))] ← +1
  FIN POUR
  POUR chaque appel y de R FAIRE
    compte_R[(y.nom, sérialiser_trié(y.arguments))] ← +1
  FIN POUR
  TP ← Σ sur chaque clé c de min(compte_A[c], compte_R[c])
  FP ← |R| − TP ; FN ← |A| − TP
  RETOURNER 2·TP / (2·TP + FP + FN)
```

**Complexité :** avec m = |A| + |R| appels et des arguments de taille L, la sérialisation triée coûte O(L log L) par appel (tri des clés, puis écriture), soit O(m·L log L) au total ; les insertions dans les dictionnaires et l'intersection coûtent O(m) en moyenne. La mémoire est en O(m·L) pour les clés.

**Du squelette au code :** `sérialiser_trié` est `cle_appel` ; les deux boucles d'insertion sont les deux `Counter(...)` de `tool_call_f1` ; la somme des minimums est `sum((a & r).values())` ; FP, FN et le F1 sont délégués à `precision_rappel_f1`, qui renvoie aussi `None` quand les deux listes sont vides.

## Cas d'usage réels aux Émirats

Les volumes, seuils et scores ci-dessous sont illustratifs ; les règles citées sont à confirmer avec le texte en vigueur avant toute réponse à un client.

### RH — un salarié en période d'essai peut-il poser des congés ?

Un cabinet RH multi-émirats déploie un agent qui répond aux salariés de ses clients : « je suis en période d'essai à Dubaï, puis-je prendre des congés ? ». L'agent doit appeler `rechercher_politique(pays="AE", theme="periode_essai")`, puis `verifier_eligibilite()` avec l'ancienneté du salarié, et répondre en ne citant que ce que la politique récupérée contient. L'équipe mesure trois choses sur 200 conversations de test : le Tool Call F1 (un appel sur le pays d'origine du salarié au lieu des EAU est un faux positif, comme dans le programme), la Faithfulness de la réponse (une condition inventée, « immédiatement », est une affirmation non justifiée), et l'Agent Goal Accuracy (le salarié a-t-il reçu une réponse actionnable, oui ou non avec les conditions ?). Si la Faithfulness chute après un changement du prompt système, la barrière d'intégration continue de l'étape 13 bis refuse le déploiement. Sans ces trois mesures, un agent qui appelle le bon outil mais déforme la règle passerait pour fiable. On suit les trois scores par version, avec leur intervalle de Wilson.

### BTP — une facture conforme, champ par champ

Un groupe de construction à Dubaï fait préparer par un agent les factures de ses sous-traitants à partir des devis et des situations de travaux. Chaque facture doit contenir des champs obligatoires : numéro d'enregistrement TVA du fournisseur, montant hors taxe, TVA à 5 %, total, retenue de garantie, référence du marché. L'équipe définit une métrique propre au métier, la complétude, égale au nombre de champs présents et justes divisé par le nombre de champs obligatoires, et la place à côté de la Faithfulness des montants par rapport au devis récupéré. Une facture de 120 000 AED hors taxe doit porter une TVA de 6 000 AED : une TVA calculée sur le montant après retenue est une affirmation non justifiée par les règles récupérées. Les métriques génériques ne voient pas un champ obligatoire absent ; la complétude, si. On suit la complétude moyenne, le nombre de factures rejetées par la comptabilité et la Faithfulness des montants.

### Assurance — 50 sinistres ne suffisent pas pour certifier 0,90

Un assureur auto construit un jeu de référence de 50 sinistres annotés, avec pour chacun la décision attendue et les clauses pertinentes. Il exige un Recall@5 du retrieval et une Faithfulness de la justification d'au moins 0,90 avant la mise en production, sur la **borne basse** de l'intervalle de Wilson (étapes 7 et 13 bis), pas sur le score brut. Avec 46 dossiers réussis sur 50, le score brut vaut 0,92, mais l'intervalle de Wilson est [0,812 ; 0,968] : la borne basse est sous le seuil. Même à 95 % de réussite observée, il faut environ 140 sinistres (133 sur 140) pour que la borne basse dépasse 0,90. L'assureur agrandit donc son jeu de référence avec des sinistres réels anonymisés plutôt que de baisser son exigence. Sans cette lecture statistique, un jeu trop petit aurait laissé passer un agent dont le vrai taux pouvait être de 0,81. On suit la borne basse de Wilson à chaque version et la taille du jeu.

### Banque — fidélité réglementaire et métriques de sécurité

Une banque de détail de Dubaï déploie un agent qui explique aux clients pourquoi leur demande de prêt personnel est acceptée ou refusée. Les réponses doivent rester fidèles aux règles récupérées, par exemple le ratio d'endettement total plafonné à 50 % du revenu par la CBUAE : une Faithfulness basse sur ce sujet est un risque de conformité, pas seulement de qualité. La banque ajoute deux métriques de sécurité absentes de RAGAS : le taux de réponses qui contiennent une donnée personnelle non masquée (IBAN, numéro d'Emirates ID, téléphone en +971), et le taux de réponses qui révèlent l'information d'un autre client. Les deux doivent valoir zéro sur le jeu de test, et la moindre occurrence bloque le déploiement, quel que soit le reste. Sans ces métriques, un agent fidèle et pertinent pourrait recopier dans sa réponse l'IBAN complet trouvé dans le dossier. On suit la Faithfulness sur les questions réglementaires et les deux taux de fuite, à chaque version.

### Secteur public — trouver le maillon faible d'un assistant bilingue

Une entité de services publics en ligne, accessible par UAE Pass, voit baisser la satisfaction de son assistant bilingue sur les démarches d'état civil. L'équipe calcule le profil complet sur 300 questions de test, en arabe et en anglais. En anglais, Context Precision et Faithfulness sont hautes. En arabe, la Context Precision est basse alors que la Faithfulness reste haute : la génération est fidèle, mais à de mauvais morceaux. C'est la première ligne du tableau de diagnostic : le problème est dans le retriever, pas dans le modèle. L'équipe corrige la normalisation de l'arabe avant l'indexation (alef, ta marbuta, diacritiques) et la Context Precision remonte. Sans le profil, elle aurait changé de LLM, ce qui n'aurait rien réparé. On suit les métriques séparément par langue, parce qu'une moyenne globale cachait le problème.

### Crypto — une baisse qui n'est que du bruit de juge

Une plateforme d'actifs virtuels agréée par la VARA mesure la Faithfulness de son agent de support avec un LLM juge. Une nouvelle version obtient 0,70 au lieu de 0,75, et l'équipe s'apprête à la rejeter. Avant cela, elle fait passer cinq fois le juge sur la même version : les scores vont de 0,65 à 0,75, d'écart-type 0,045, comme dans le programme. La différence entre les deux versions est du même ordre que la dispersion du juge, et le bruit d'un juge tire même le score vers 0,5 (démonstration, point 6). L'équipe fige donc la version du juge, sa température et son prompt, répète chaque mesure cinq fois, compare les versions avec McNemar sur les mêmes cas (étape 13 bis) et calibre le juge sur 100 affirmations annotées par des humains. Sans cette discipline, elle aurait rejeté une bonne version, ou accepté une mauvaise, sur un tirage au sort. On suit la moyenne et l'écart-type des scores, et l'accord du juge avec les humains.

## Pièges et limites

- **Croire un juge LLM déterministe.** Il échantillonne ; son bruit disperse le score et le biaise vers 0,5. Fixer version, température et prompt, répéter, publier la dispersion, calibrer contre des humains.
- **Confondre Tool Call F1 et ToolCallAccuracy.** Le premier ignore l'ordre, la seconde le compte. Choisir selon le métier, et publier les deux si l'ordre a un sens.
- **Comparer des appels avec un ensemble.** Un ensemble efface les doublons ; un `Counter` les compte comme des faux positifs.
- **Lire une Context Precision seule.** Elle ne voit pas les morceaux pertinents jamais ramenés : il faut le Context Recall à côté.
- **Mélanger les conventions.** Aucune affirmation donne `None` (indéfini) ; aucun morceau pertinent parmi K donne 0 (échec) ; ces deux cas ne se moyennent pas de la même façon.

### Exercice feuille blanche

1. Sans regarder le code, écrire `context_precision`, puis calculer à la main v = (0, 1, 0, 1). (Réponse : (1/2 + 2/4)/2 = 0,5.)
2. Prédire, puis vérifier : un juge à 20 % d'erreur juge une réponse dont la vraie fidélité vaut 0,9. Quelle fidélité mesurera-t-il en moyenne ? (Réponse : 0,2 + 0,6 × 0,9 = 0,74.)
3. Trouver le bug : une variante remplace les `Counter` par des ensembles, avec `tp = len(set(A) & set(R))`, `fp = len(set(R)) - tp` et `fn = len(set(A)) - tp`, où A et R sont les listes de clés produites par `cle_appel`. Que vaut-elle quand l'agent appelle deux fois `rechercher_politique(pays="AE", …)` et jamais `verifier_eligibilite()` ? (Réponse : TP = 1, FP = 0, FN = 1, donc 0,667 au lieu de 0,5 : l'appel en double a disparu.)

## Pour aller plus loin

- Si l'on connaît le taux d'erreur ε du juge, on peut corriger le score : F = (E[F̂] − ε)/(1 − 2ε), à condition que ε soit nettement inférieur à 0,5.
- RAGAS propose aussi des variantes de Context Precision avec ou sans réponse de référence, et des juges qui notent sur une échelle au lieu d'un oui ou non ; la formule ci-dessus suppose des vₖ binaires.
- Les démonstrations complètes de ce chapitre sont réparties : Faithfulness à l'étape 54, Answer Relevancy à l'étape 55, Context Precision à l'étape 57, Tool Call F1 à l'étape 59, et un recueil de théorèmes à l'étape 64 bis.

> Suite : [Faithfulness](<54-Evaluation-Formule-Faithfulness.md>) — étape 54.
