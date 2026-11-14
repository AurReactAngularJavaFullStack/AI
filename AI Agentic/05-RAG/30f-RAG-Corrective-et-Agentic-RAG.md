# Étape 30 sexies — RAG — Corrective RAG et Agentic RAG

**Dossier :** 05-RAG

> Étape 30 sexies du parcours · Prérequis : [Index ANN : HNSW, IVF et PQ](<30e-RAG-Index-ANN-HNSW-IVF-PQ.md>) · Suite : [GraphRAG et mémoire en graphe](<30g-RAG-GraphRAG-et-Memoire-en-Graphe.md>)

## Définition

Un RAG classique récupère une fois, puis génère, quoi que la récupération ait ramené : si les passages sont hors sujet, le modèle invente ou répond à côté. Le **Corrective RAG** (CRAG, Yan et al., 2024) ajoute un **évaluateur de récupération** entre la recherche et la génération. Il note chaque passage et range le résultat dans l'une de trois zones. **Correct** : au moins un passage dépasse un seuil haut τ⁺ ; on **raffine** alors, en découpant les passages en phrases et en ne gardant que les phrases pertinentes (« décomposer puis recomposer »). **Incorrect** : tous les passages restent sous un seuil bas τ⁻ ; on les écarte et l'on **bascule** sur une autre source, une recherche web dans l'article. **Ambigu** : entre les deux ; on garde le raffinage et l'on ajoute la recherche externe. Le **Self-RAG** (Asai et al., 2023) pousse l'idée dans le modèle lui-même. Celui-ci est entraîné à émettre des **jetons de réflexion** : Retrieve (faut-il chercher ?), IsRel (ce passage est-il pertinent ?), IsSup (ma phrase est-elle soutenue par le passage ?) et IsUse (la réponse est-elle utile, de 1 à 5). La génération choisit ensuite les segments les mieux notés. Enfin, l'**Agentic RAG** fait de la recherche un ensemble d'outils parmi lesquels l'agent choisit, tour après tour, dans la boucle canonique : ici `chercher_base`, `chercher_web` et `demander_precision`, avec un budget et des critères d'arrêt explicites.

## Rôle dans un agent

Le RAG correctif intervient entre **agir** et **observer**. L'agent appelle l'outil de recherche ; avant que le résultat ne revienne au modèle, du code déterministe l'évalue et le raffine, et le modèle observe un verdict (correct, ambigu, incorrect) avec les seules phrases retenues. C'est un garde-fou **de contexte**, placé avant la génération. Il complète le garde-fou de sortie de l'étape 29, qui vérifie la réponse une fois écrite. Le modèle **décide** ensuite de la suite : répondre, chercher ailleurs, demander une précision à l'utilisateur, ou s'abstenir. Trois règles du parcours s'appliquent. Le budget de recherche externe est tenu **dans l'outil**, qui refuse au-delà, au lieu de retirer l'outil de la liste (code canonique). Une action répétée à l'identique arrête la boucle (statut « boucle »). Enfin, le nombre total d'étapes est plafonné par `max_etapes`. Pour rester indépendant d'un framework, il suffit de trois fonctions (rechercher, évaluer, raffiner) et d'une politique : l'évaluateur est un port, que l'on peut remplir par le score lexical de ce fichier, par le cross-encodeur de l'étape 30 bis ou par un petit modèle juge.

## Équation complète

Score de l'évaluateur (jouet de ce fichier) : la part des termes de la question présents dans le passage, nulle si la question nomme une entité que le passage ne nomme pas :

$$
\phi(q, d) = \begin{cases} 0 & \text{si } E(q) \not\subseteq T(d) \\ \dfrac{\lvert T(q) \cap T(d) \rvert}{\lvert T(q) \rvert} & \text{sinon} \end{cases}
$$

Verdict sur l'ensemble D des passages récupérés (avec la convention max ∅ = 0) :

$$
v(q, D) = \begin{cases} \text{correct} & \text{si } \max_{d \in D} \phi(q, d) \ge \tau^{+} \\ \text{incorrect} & \text{si } \max_{d \in D} \phi(q, d) < \tau^{-} \\ \text{ambigu} & \text{sinon} \end{cases}
$$

Raffinage : on ne garde que les phrases u des passages dont le score atteint τₚ :

$$
R(q, D) = \{\, u \;:\; u \text{ phrase d'un } d \in D ,\; \phi(q, u) \ge \tau_p \,\}
$$

Probabilité d'une réponse juste avec repli, cas particulier de l'évaluateur parfait, gain et seuil de fausses alarmes :

$$
P(\text{juste}) = g \big[ (1 - f)\, a + f \, w \big] + (1 - g)\, s \, w
$$

$$
P(\text{juste}) = g + (1 - g)\, w \qquad \text{si } s = 1,\; f = 0,\; a = 1
$$

$$
\Delta = P(\text{juste}) - g\, a = (1 - g)\, s\, w - g\, f\, (a - w) , \qquad f^{*} = \frac{(1 - g)\, s\, w}{g\, (a - w)}
$$

Coût attendu :

$$
\mathbb{E}[\text{coût}] = c_1 + c_2 + \big( g f + (1 - g) s \big)\, c_3
$$

Budget de B replis indépendants, avec un évaluateur parfait :

$$
P_B(\text{juste}) = g + (1 - g)\big( 1 - (1 - w)^B \big) , \qquad \mathbb{E}[\text{replis}] = (1 - g)\, \frac{1 - (1 - w)^B}{w}
$$

## Décryptage des symboles

$$
q,\; d,\; D
$$

La question, un passage et l'ensemble des passages renvoyés par la recherche (au plus 3 dans la base, 2 sur le web) ; variables `question`, `passages`, `trouves`.

$$
T(x),\; E(q)
$$

L'ensemble des termes d'un texte, après minuscules, accents retirés, mots vides retirés et pluriel en « s » retiré, et l'ensemble des entités nommées par la question (émirats, zones franches) ; fonction `termes(x)` et ensemble `ENTITES`.

$$
\phi(q, d)
$$

Le score de l'évaluateur, un réel de [0 ; 1] ; fonction `couverture(question, passage)`. C'est un jouet lexical qui tient la place d'un modèle entraîné.

$$
\tau^{+},\; \tau^{-},\; \tau_p
$$

Le seuil haut (0,6), le seuil bas (0,3) et le seuil de raffinage des phrases (0,3), illustratifs et à calibrer, avec 0 ≤ τ⁻ ≤ τ⁺ ≤ 1 ; constantes `TAU_HAUT`, `TAU_BAS`, `TAU_PHRASE`.

$$
v(q, D),\; R(q, D)
$$

Le verdict, l'une des trois chaînes « correct », « ambigu » ou « incorrect », et les phrases retenues avec leur source ; fonctions `verdict(score_max)` et `raffiner(question, passages)`.

$$
g,\; a
$$

La probabilité qu'une récupération soit bonne (le passage utile est dans D) et la probabilité que la réponse soit juste quand le bon contexte est gardé ; réels de [0 ; 1] ; paramètres `g` et `a`.

$$
s,\; f
$$

La sensibilité de l'évaluateur, probabilité de donner l'alerte (verdict autre que correct) sur une mauvaise récupération, et son taux de fausses alarmes, probabilité de donner l'alerte sur une bonne ; paramètres `s` et `f`.

$$
w
$$

La probabilité que le repli (la recherche externe) mène à une réponse juste ; paramètre `w`.

$$
c_1,\; c_2,\; c_3
$$

Le coût d'une recherche dans la base, celui de l'évaluation et celui d'un repli, en unités illustratives (tokens, latence ou AED) ; paramètres `c1`, `c2`, `c3`, et le dictionnaire `COUTS` pour les scénarios.

$$
B,\; \Delta,\; f^{*}
$$

Le nombre maximal de replis, le gain de justesse apporté par la correction, et le taux de fausses alarmes au-delà duquel ce gain devient négatif ; paramètre `budget` (`budget_web` dans l'outil).

## Démonstration

### 1. La probabilité d'une réponse juste, par les probabilités totales

On découpe les questions en quatre cas qui ne se recouvrent pas et couvrent tout : la récupération est bonne ou mauvaise, et l'évaluateur donne l'alerte ou non. On fait trois hypothèses, que le code reprend. Après une alerte, la réponse vient du repli et réussit avec la probabilité w, quelle que soit la raison de l'alerte. Une mauvaise récupération qui passe sans alerte donne une réponse fausse ; c'est une hypothèse prudente, car le modèle peut parfois connaître la réponse, mais on ne compte pas sur la chance. Enfin, une bonne récupération gardée donne une réponse juste avec la probabilité a.

| Cas | Probabilité du cas | Réponse juste avec la probabilité |
|---|---|---|
| bonne récupération, pas d'alerte | g (1 − f) | a |
| bonne récupération, alerte (fausse alarme) | g f | w |
| mauvaise récupération, alerte (détection) | (1 − g) s | w |
| mauvaise récupération, pas d'alerte (ratée) | (1 − g)(1 − s) | 0 |

Les quatre probabilités des cas somment à g + (1 − g) = 1. Par la formule des probabilités totales, P(juste) est la somme, sur les quatre cas, de la probabilité du cas multipliée par la probabilité d'une réponse juste dans ce cas, ce qui donne la formule de l'équation complète. Avec un évaluateur parfait (s = 1, f = 0) et a = 1, il reste g + (1 − g) w : la récupération réussit, ou elle échoue et le repli corrige. Le RAG simple correspond à s = f = 0 : il n'y a jamais d'alerte, et P(juste) = g a.

Avec g = 0,8, a = 1, s = 0,9, f = 0,1 et w = 0,7 :

$$
P(\text{juste}) = 0{,}8 \times (0{,}9 \times 1 + 0{,}1 \times 0{,}7) + 0{,}2 \times 0{,}9 \times 0{,}7 = 0{,}776 + 0{,}126 = 0{,}902
$$

contre 0,8 pour le RAG simple et 0,8 + 0,2 × 0,7 = 0,94 pour un évaluateur parfait. Le programme retrouve ces nombres, puis tire 60 000 questions selon le même arbre : il mesure 0,9023.

### 2. Les fausses alarmes peuvent rendre la correction nuisible

On développe le gain par rapport au RAG simple :

$$
\Delta = g(1 - f)a + g f w + (1 - g) s w - g a = (1 - g)\, s\, w - g\, f\, (a - w)
$$

Le premier terme est ce que rapportent les détections : une question mal servie sur cinq, détectée 9 fois sur 10 et corrigée 7 fois sur 10. Le second est ce que coûtent les fausses alarmes : quand le repli est moins bon que la base (w < a), chaque fausse alarme remplace une bonne réponse probable par une réponse moins sûre. Δ diminue donc linéairement avec f, et il devient négatif au-delà de f* :

$$
f^{*} = \frac{0{,}2 \times 0{,}9 \times 0{,}7}{0{,}8 \times (1 - 0{,}7)} = \frac{0{,}126}{0{,}24} = 0{,}525
$$

Avec un évaluateur trop sévère, qui donne l'alerte sur 60 % des bonnes récupérations, P(juste) = 0,8 × (0,4 + 0,6 × 0,7) + 0,126 = 0,782, sous les 0,8 du RAG simple : le programme le vérifie. Inversement, si le repli est au moins aussi bon que la base (w ≥ a), le second terme est nul ou positif, et les fausses alarmes ne coûtent plus que de l'argent.

### 3. Le coût attendu

Le repli est déclenché exactement quand l'évaluateur donne l'alerte, ce qui arrive avec la probabilité g f + (1 − g) s, encore par les probabilités totales : 0,8 × 0,1 + 0,2 × 0,9 = 0,26. Avec des coûts illustratifs c₁ = 1 pour la recherche dans la base, c₂ = 0,2 pour l'évaluation et c₃ = 3 pour un repli :

$$
\mathbb{E}[\text{coût}] = 1 + 0{,}2 + 0{,}26 \times 3 = 1{,}98
$$

contre 1 pour le RAG simple. La correction double presque le coût moyen pour 10,2 points de justesse : chaque réponse juste gagnée coûte 0,98 / 0,102 ≈ 9,6 unités. C'est le chiffre à comparer au coût d'une erreur dans le métier concerné.

### 4. Un budget de replis : des rendements décroissants

Supposons l'évaluateur parfait et autorisons jusqu'à B replis, chacun réussissant avec la probabilité w indépendamment des autres. La probabilité qu'au moins un des B replis réussisse est 1 − (1 − w)ᴮ, la formule des essais répétés de l'[étape 11](<../03-Schemas-Outils-et-Premiere-Evaluation/11-Schemas-Formule-Taux-de-Validation.md>), d'où P_B. Le gain apporté par un repli de plus vaut

$$
P_{B+1} - P_B = (1 - g)\, w\, (1 - w)^B
$$

qui décroît strictement avec B quand 0 < w < 1 : 0,14, puis 0,042, puis 0,0126 pour g = 0,8 et w = 0,7. La courbe de justesse est donc concave, et chaque repli supplémentaire rapporte moins que le précédent. Le j-ième repli n'a lieu que si les j − 1 premiers ont échoué, ce qui arrive avec la probabilité (1 − w)ʲ⁻¹. En sommant cette série géométrique, le nombre moyen de replis par question vaut

$$
(1 - g) \sum_{j=0}^{B-1} (1 - w)^j = (1 - g)\, \frac{1 - (1 - w)^B}{w}
$$

Pour B = 1, 2 et 3, cela donne une justesse de 0,94, 0,982 et 0,9946, pour 0,2, 0,26 et 0,278 replis en moyenne, et la simulation retrouve chaque valeur à moins de 0,01. Le coût moyen reste borné par (1 − g)/w quand B grandit, mais pas la latence du pire cas, qui croît avec B : d'où un budget explicite.

L'hypothèse d'indépendance est la plus fragile. Renvoyer la même requête au même moteur échoue de la même façon : les échecs sont alors corrélés, et la formule surestime le gain. C'est pourquoi la politique du programme reformule sa requête au second essai, et pourquoi la boucle canonique arrête un appel répété à l'identique. Le programme le vérifie (bloc 5) : statut « boucle » après 2 étapes et un seul appel exécuté.

### 5. Les seuils déplacent les verdicts dans un seul sens

À scores fixés, monter τ⁺ rend la condition « correct » plus exigeante : l'ensemble des récupérations jugées correctes rétrécit, et celles qui en sortent deviennent ambiguës. Monter τ⁻ agrandit de même l'ensemble des récupérations jugées incorrectes. La probabilité d'alerte ne peut donc que croître avec τ⁺, et avec elle s et f à la fois. Il n'existe pas de réglage qui améliore les deux : on choisit τ⁺ pour garder f sous f* (point 2) tout en gardant s assez haut.

**Exemple fait à la main.** La question « Quels frais de transfert le DLD prélève-t-il sur la vente d'un bien à Dubaï Marina ? » a huit termes : frai, transfert, dld, preleve, vente, bien, dubai, marina. La première phrase du document immo-01 en contient sept, tous sauf « marina » : φ = 7/8 = 0,875. La seconde phrase, sur le paiement, ne nomme pas Dubaï : la contrainte d'entité lui donne 0 (sans cette contrainte, elle aurait 1/8 = 0,125, pour le seul mot « transfert »). Avec τ⁺ = 0,6, le verdict est correct : un seul appel, coût 1, et une réponse qui ne garde que la phrase utile. Avec τ⁺ = 0,9, le même passage devient ambigu. L'agent va alors sur le web, où la seule page trouvée est un forum qui ne nomme pas Dubaï (score 0, verdict incorrect). Sa reformulation est refusée par le budget, et il s'abstient : coût 4, et une bonne réponse perdue. C'est une fausse alarme, avec ses deux prix, celui du point 2 et celui du point 3.

### 6. Le raffinage écarte la règle qui ne s'applique pas

Pour « Comment calculer l'indemnité de fin de service d'un salarié du DIFC ? », la recherche dans la base ramène deux passages. Le premier, rh-02, dit que les salariés du DIFC relèvent d'un régime d'épargne propre, DEWS : il couvre indemnite, salarie et difc, soit φ = 3/6 = 0,5. Le second, rh-01, donne la règle fédérale des 21 et 30 jours : il couvre indemnite, fin et service, soit aussi 0,5 sans contrainte d'entité, mais il ne nomme pas le DIFC et tombe à 0. Le meilleur score, 0,5, est entre τ⁻ et τ⁺ : verdict ambigu. L'agent garde rh-02 et cherche sur le web, où la page simulée sur DEWS obtient 4/6 ≈ 0,667, verdict correct. Sans la contrainte d'entité, la règle fédérale entrerait dans le contexte avec le même score que la bonne règle, et le modèle pourrait calculer 21 jours par année pour un salarié qui n'y a pas droit. Une contrainte dure sur les entités est plus fiable qu'un score de recouvrement, parce qu'elle ne se laisse pas compenser par d'autres mots communs.

## Effets et comportement

- **Monter τ⁺** déclenche plus de replis : la sensibilité monte, les fausses alarmes aussi, le coût croît, et la justesse monte puis baisse quand f dépasse f* (points 2 et 5).
- **Monter τ⁻** fait passer des récupérations d'« ambigu » à « incorrect » : la base est alors écartée en entier au lieu d'être combinée avec le repli.
- **Monter τₚ** raccourcit le contexte et le rend plus net, au risque d'écarter une phrase nécessaire, par exemple une exception écrite sans les mots de la question.
- **Augmenter B** fait monter la justesse de façon concave (point 4) ; le coût moyen reste borné, mais la latence du pire cas croît.
- **La qualité du repli w** décide de tout. Un web ouvert, avec ses forums et ses pages périmées, a un w faible : le repli corrige peu et les fausses alarmes deviennent nuisibles. On restreint le repli à des sources officielles connues.
- **Demander une précision** coûte un tour à l'utilisateur, mais vaut la peine quand l'information manquante change la réponse, comme l'émirat d'un bien.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| T(x), E(q) | `termes(x)`, `ENTITES` |
| φ(q, d) | `couverture(question, passage)` |
| τ⁺, τ⁻, τₚ | `TAU_HAUT`, `TAU_BAS`, `TAU_PHRASE` (ou `tau_haut`, `tau_bas`) |
| v(q, D) | `verdict(score_max, tau_haut, tau_bas)` |
| R(q, D) | `raffiner(question, passages)` |
| recherche puis évaluation | `rechercher(corpus, requete, k)`, puis `evaluer_et_raffiner(...)` |
| g, a, s, f, w | `g`, `a`, `s`, `f`, `w` |
| P(juste) | `p_juste(g, a, s, f, w)` |
| E[coût] | `cout_attendu(g, s, f, c1, c2, c3)` |
| P_B(juste), E[replis] | `p_juste_budget(g, w, budget)`, `replis_attendus(g, w, budget)` |
| B | `budget_web` dans `fabriquer_outils` |
| politique de l'agent | `LLMRegles.create(...)` dans `executer_agent` |

### Déroulé, ligne par ligne

**Code canonique recopié.** `Bloc`, `Reponse`, `texte`, `appel_outil`, `FakeLLM` et `executer_agent` forment le port LLM et la boucle du parcours, tels quels. `idf_bm25` et `bm25_score` sont ceux de l'étape 22. La même boucle tournera avec l'adaptateur Claude du parcours, sans changement (extrait plus bas).

**`p_juste(g, a, s, f, w)`** refuse toute probabilité hors de [0 ; 1] puis applique l'arbre du point 1 : `g * ((1 - f) * a + f * w) + (1 - g) * s * w`. Pour `(0.8, 1.0, 0.9, 0.1, 0.7)`, elle renvoie 0,902. **`cout_attendu`** ajoute aux coûts fixes `c1 + c2` le coût du repli multiplié par la probabilité d'alerte, soit 1,98 pour les coûts `1.0`, `0.2` et `3.0`. **`p_juste_budget`** et **`replis_attendus`** sont les deux formules du point 4.

**`simuler(n, g, a, s, f, w, budget, rng)`** rejoue l'arbre question par question avec un `random.Random` à graine fixe. `bonne` tire la qualité de la récupération ; `alerte` tire la décision de l'évaluateur avec la probabilité `f` ou `s` selon le cas ; sans alerte, la réponse est juste si la récupération était bonne et si le tirage contre `a` réussit ; avec alerte, la boucle tente jusqu'à `budget` replis et s'arrête au premier succès. La fonction renvoie la part de réponses justes et le nombre moyen de replis.

**`termes(t)`** passe en minuscules, décompose le texte (`unicodedata.normalize("NFKD", ...)`) pour retirer les accents, garde les suites de lettres et de chiffres, retire les mots vides et le « s » final des mots de plus de trois lettres : « Fujaïrah » devient `fujairah`, « frais » devient `frai`.

**`couverture(question, passage)`** calcule les deux ensembles de termes, renvoie 0 si une entité de la question manque au passage (`(q & ENTITES) - p` non vide), et sinon la part des termes de la question présents dans le passage. Une question vide après normalisation lève `ValueError`.

**`verdict(score_max, tau_haut, tau_bas)`** vérifie 0 ≤ τ⁻ ≤ τ⁺ ≤ 1, puis applique les trois zones : 0,875 donne « correct » avec τ⁺ = 0,6 et « ambigu » avec τ⁺ = 0,9. **`phrases(t)`** coupe après un point, un point d'exclamation ou un point d'interrogation suivi d'un blanc. **`raffiner`** garde chaque phrase dont la couverture atteint τₚ, avec l'identifiant de sa source.

**`rechercher(corpus, requete, k)`** classe les documents par BM25 (étape 22), égalités départagées par l'identifiant, ne garde que les scores positifs et coupe à k. **`evaluer_et_raffiner`** note chaque passage, prend le meilleur score (0 si rien n'a été trouvé), en déduit le verdict, et ne raffine que si le verdict n'est pas « incorrect ». Elle renvoie un dictionnaire `verdict`, `score_max`, `passages`, `retenus`, que le modèle reçoit en JSON.

**`BASE` et `WEB`** sont les deux corpus. La base contient huit documents internes qui reprennent les règles vérifiées du parcours (frais de transfert du DLD, endettement, prêt personnel, TVA, impôt sur les sociétés, fin de service et régime du DIFC). Le web simulé contient quatre pages : l'indexation de l'AED sur l'USD, une page sur DEWS, un forum qui avance un faux chiffre et un guide touristique. Les pages sont fictives ; seuls les chiffres réglementaires viennent de la liste vérifiée.

**`fabriquer_outils(reponses_utilisateur, budget_web, tau_haut, tau_bas)`** crée les trois outils autour d'un état partagé `etat`. `chercher_base` cherche les 3 meilleurs documents internes puis les évalue. `chercher_web` vérifie d'abord le budget (`if etat["web"] >= budget_web`), refuse au-delà avec un message, et sinon cherche les 2 meilleures pages. `demander_precision` renvoie la réponse suivante de l'utilisateur simulé.

**`LLMRegles.create(...)`** joue le rôle du modèle : il relit l'historique (les blocs `tool_use` déjà émis et les résultats d'outils) et choisit l'action suivante.

- Premier tour : si la question parle de frais, de bail ou de location sans nommer d'émirat, il appelle `demander_precision` ; sinon `chercher_base` avec la question.
- Après une précision, il cherche dans la base avec la question complétée par la réponse : « … Abu Dhabi ».
- Après la base, si le verdict n'est pas « correct », il appelle `chercher_web` avec la même requête.
- Après un refus de budget, il s'abstient.
- Si aucune source n'est jugée correcte, il reformule une fois (les termes clés seuls, par exemple `frai transfert appartement abu dhabi`) puis s'abstient.
- Sinon, il répond en recopiant les phrases retenues des sources correctes et ambiguës, chacune suivie de sa source entre crochets.

**`lancer(question, ...)`** fabrique les outils, lance `executer_agent` avec `LLMRegles()` et au plus 6 étapes. Il calcule ensuite le coût (un appel refusé ne coûte rien) et la liste des verdicts dans l'ordre.

**`main()`**, bloc par bloc.

1. Les nombres des points 1 à 3 : 0,902, 0,94 et 1,98, puis la simulation de 60 000 questions et l'évaluateur trop sévère (0,782 < 0,8).
2. Le budget : pour B = 1, 2, 3, la formule et la simulation, à moins de 0,01 l'une de l'autre, puis la décroissance des gains.
3. L'exemple à la main du point 5 : les huit termes, les couvertures 0,875 et 0, et les deux verdicts.
4. Six scénarios. Le dictionnaire `attendu` vérifie pour chacun la suite exacte des outils et des verdicts, puis les `assert` vérifient le contenu des réponses. La réponse correcte garde la phrase des 4 % et écarte celle du paiement. La réponse sur le change cite le taux de 3,6725. La réponse sur le DIFC cite rh-02 et web-02 mais pas rh-01. Les trois autres sont des abstentions, sans la règle de Dubaï pour un bien d'Abu Dhabi, et le seuil trop sévère coûte plus cher que le bon réglage.
5. Un faux LLM scripté renvoie deux fois le même appel `chercher_web` : la boucle canonique s'arrête avec le statut « boucle ». Deux couples de seuils incohérents sont refusés par `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fabrique du port LLM canonique joue le secrétaire qui glisse une phrase dans une enveloppe standard : elle reçoit une chaîne de caractères et renvoie un `Bloc` de type « text » qui la contient, sans rien vérifier. Le faux LLM à règles s'en sert pour toutes ses réponses finales, qu'il s'agisse d'une réponse citée ou de la phrase d'abstention, et la boucle `executer_agent` en recolle le contenu pour former la réponse de l'agent.

**`appel_outil(nom, arguments, id_)`** — Celle-ci remplit le bon de commande que le modèle adresse à un outil : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant d'appel, et renvoie un `Bloc` de type « tool_use » qui porte ces trois informations. Le faux LLM à règles l'utilise pour demander une précision, chercher dans la base ou chercher sur le web, et la boucle canonique lit ce bloc pour savoir quelle fonction lancer et avec quels paramètres.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui ne connaît que son texte, réplique après réplique : il reçoit la liste des réponses prévues, en garde une copie pour que le scénario d'origine ne soit pas modifié, et met à zéro le compteur `appels`, sans rien renvoyer. Dans ce programme, il ne sert qu'au point 5, où son script contient deux fois le même appel à `chercher_web`, pour vérifier que la boucle canonique repère la répétition.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode imite la signature d'un vrai modèle, avec ses trois arguments nommés, mais se contente de lire la réplique suivante du script, sans regarder ni la consigne, ni l'historique, ni les outils : elle lève `RuntimeError` si le script est épuisé, et sinon renvoie la `Reponse` prévue en avançant son compteur. C'est ce qui permet au point 5 de rejouer à l'identique deux appels de repli et de constater que la boucle s'arrête après le premier.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est le régisseur canonique du parcours, la boucle qui fait alterner le modèle et les outils : il reçoit le modèle, la consigne système, la question, le dictionnaire des outils, leurs schémas et un nombre maximal d'étapes, huit par défaut et six dans `lancer`. À chaque tour, il interroge le modèle et recopie sa réponse telle quelle, s'arrête sur un refus ou une troncature, recommence sur une pause, renvoie le texte final quand le modèle n'appelle plus d'outil, s'arrête avec le statut « boucle » si la même action revient deux fois de suite avec les mêmes arguments, et sinon exécute les outils en renvoyant les erreurs au modèle. Il renvoie un dictionnaire avec le statut, la trace des appels, le nombre d'étapes et, en cas de succès, la réponse.

**`idf_bm25(n_t, n_docs)`** — C'est le crieur canonique de l'étape 22, qui annonce le poids d'un mot d'après sa rareté dans un corpus : la fonction reçoit le nombre de documents qui contiennent le terme et le nombre total de documents, huit pour la base interne et quatre pour le web simulé, puis renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), toujours positif. Elle n'est appelée que par `bm25_score`, pour que « DLD » ou « DIFC » pèsent davantage qu'un mot présent dans plusieurs documents.

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est le juge lexical canonique de l'étape 22, qui note un document pour une requête : la fonction reçoit la requête et le document sous forme de listes de termes, le corpus entier et les réglages k1 = 1,5 et b = 0,75 par défaut, puis additionne, pour chaque terme présent, son IDF multiplié par une partie fréquence saturée et corrigée par la longueur. Elle renvoie ce score, dont `rechercher` se sert pour classer les documents et ne garder que ceux qui partagent au moins un terme avec la question.

**`cout_attendu(g, s, f, c1, c2, c3)`** — Cette fonction est le comptable qui chiffre d'avance ce que coûtera la politique corrective : elle reçoit la probabilité g d'une bonne récupération, la probabilité s de détecter une mauvaise récupération, la probabilité f d'une fausse alerte, et les coûts c1 de la recherche, c2 de l'évaluateur et c3 du repli. Elle renvoie c1 + c2 plus la probabilité de repli, g f + (1 − g) s, multipliée par c3 ; avec g = 0,8, s = 0,9, f = 0,1 et les coûts 1, 0,2 et 3, la probabilité de repli vaut 0,26 et le coût attendu 1,98, contre 1 pour un RAG simple.

**`p_juste_budget(g, w, budget)`** — Elle calcule la chance de finir par une réponse juste quand on autorise plusieurs tentatives de repli, comme un pêcheur qui s'accorde B lancers de plus : la fonction reçoit la probabilité g d'une bonne récupération, la probabilité w de succès d'un repli et le budget B, et renvoie g + (1 − g)(1 − (1 − w)^B), pour un évaluateur parfait et des replis indépendants. Avec g = 0,8 et w = 0,7, elle donne 0,94 pour un repli et 0,9946 pour trois, et `main` vérifie que chaque repli supplémentaire rapporte moins que le précédent.

**`replis_attendus(g, w, budget)`** — Cette fonction répond à la question du gestionnaire de budget : combien de replis paiera-t-on en moyenne par question ? Elle reçoit les mêmes trois paramètres que `p_juste_budget` et renvoie (1 − g)(1 − (1 − w)^B) / w, la somme d'une série géométrique tronquée, puisqu'on s'arrête au premier repli réussi. Avec g = 0,8 et w = 0,7, elle vaut 0,2 pour un budget d'un repli et environ 0,278 pour trois ; `main` compare ces valeurs à la simulation de 60 000 questions, à moins de 0,01 près.

**`phrases(t)`** — C'est le ciseau qui coupe un passage en phrases avant le raffinage : la fonction reçoit un texte, retire ses blancs de bord, le coupe juste après chaque point, point d'exclamation ou point d'interrogation suivi d'un blanc, et renvoie la liste des phrases non vides. Sur le document `immo-01`, elle donne deux phrases, celle des 4 % prélevés par le DLD et celle du moment du paiement, dont les couvertures valent 0,875 et 0 pour la question de l'exemple à la main.

**`raffiner(question, passages, tau_phrase)`** — Cette fonction joue l'éditeur qui découpe chaque passage puis ne recolle que les phrases utiles : elle reçoit la question, la liste des passages, chacun avec son identifiant et son texte, et le seuil de phrase τₚ, 0,3 par défaut, découpe chaque passage avec `phrases`, et renvoie la liste des phrases dont la couverture atteint ce seuil, chacune accompagnée de l'identifiant de sa source. C'est ainsi que la réponse correcte garde la phrase des 4 % et écarte celle du paiement, qui ne parle pas de la question posée.

**`evaluer_et_raffiner(question, trouves, tau_haut, tau_bas)`** — C'est l'évaluateur de récupération du Corrective RAG, le contrôleur qui note chaque passage avant de décider s'il peut servir : la fonction reçoit la question, les sources trouvées et les deux seuils, calcule la couverture de chaque source, arrondie à trois décimales, prend le meilleur score, ou 0 si rien n'a été trouvé, en tire le verdict « correct », « ambigu » ou « incorrect », et ne raffine les passages que si le verdict n'est pas « incorrect ». Elle renvoie un dictionnaire avec le verdict, le meilleur score, les passages notés et les phrases retenues, que le modèle reçoit en JSON.

**`chercher_base(requete)`** — Cette fonction interne, fabriquée par `fabriquer_outils`, est le guichet de la documentation interne : elle reçoit une requête, cherche les trois meilleurs documents de `BASE` avec `rechercher`, puis les fait noter et raffiner par `evaluer_et_raffiner` avec les seuils choisis à la fabrication. Elle renvoie le dictionnaire du verdict ; elle coûte 1 unité, et pour la question sur les frais de transfert à Dubaï, elle rend aussitôt le verdict « correct », si bien que l'agent répond sans aller plus loin.

**`chercher_web(requete)`** — Cette autre fonction interne de `fabriquer_outils` est le guichet des sources externes, tenu par un employé qui surveille sa caisse : elle reçoit une requête, vérifie d'abord dans l'état partagé que le budget de recherches web n'est pas épuisé, renvoie dans ce cas un dictionnaire de refus, et sinon compte l'appel, cherche les deux meilleures pages de `WEB` et les fait évaluer et raffiner. Chaque recherche acceptée coûte 3 unités, un refus ne coûte rien ; c'est en tenant le budget dans l'outil, plutôt qu'en retirant l'outil, qu'on laisse le modèle constater le refus et s'abstenir.

**`demander_precision(question)`** — Cette troisième fonction interne de `fabriquer_outils` joue l'utilisateur à qui l'agent pose une question : elle reçoit la question de l'agent, retire de la liste des réponses prévues la première d'entre elles et la renvoie dans un dictionnaire, ou une chaîne vide si plus aucune réponse n'est prévue. Dans le scénario « précision puis abstention », elle répond « Abu Dhabi » à « Dans quel émirat se trouve le bien ? », ce qui coûte 0,5 unité et permet à l'agent de compléter sa requête.

**`LLMRegles.__init__()`** — Le constructeur prépare un faux modèle sans script, qui décide de ses actions d'après des règles écrites à la main : il ne reçoit aucun argument et met seulement à zéro le compteur `appels`, sans rien renvoyer. Contrairement à `FakeLLM`, cet objet ne connaît pas ses réponses à l'avance ; il les déduit à chaque tour de l'historique de la conversation, comme le ferait un modèle guidé par son prompt système.

**`LLMRegles.create(system, messages, tools)`** — Cette méthode est le cerveau à règles de l'agent : elle reçoit la consigne, l'historique et les outils, compte l'appel, relit la question, les appels d'outils déjà émis et leurs résultats, puis choisit l'action suivante. Au premier tour, elle demande une précision si la question parle de frais, de bail ou de location sans nommer d'émirat, et sinon cherche dans la base ; après une précision, elle cherche la question complétée ; après la base, elle va sur le web si le verdict n'est pas « correct » ; sur un refus de budget, elle s'abstient ; sans aucune source correcte, elle reformule une fois avec les termes clés puis s'abstient ; sinon, elle répond en citant les phrases retenues des sources correctes et ambiguës, chacune suivie de sa source entre crochets.

**`lancer(question, reponses_utilisateur, budget_web, tau_haut, tau_bas)`** — Cette fonction met en scène un scénario complet : elle reçoit la question, les réponses prévues de l'utilisateur, le budget de recherches web, un par défaut, et les deux seuils, fabrique les trois outils autour d'un état neuf, lance `executer_agent` avec un `LLMRegles` et au plus six étapes, puis ajoute au résultat le coût total, en comptant 1 pour la base, 3 pour le web et 0,5 pour une précision, un refus ne coûtant rien, et la liste des verdicts dans l'ordre. Elle renvoie ce dictionnaire ; les coûts vont de 1,0 pour la question correcte à 7,0 pour la question à laquelle rien ne répond.

**`main()`** — Le chef d'orchestre déroule cinq démonstrations : il calcule d'abord les probabilités 0,8, 0,902 et 0,94 et le coût 1,98, les confirme par une simulation de 60 000 questions et montre qu'un évaluateur trop sévère fait tomber la réponse juste à 0,782, puis vérifie pour un budget de un à trois replis les formules contre la simulation et la décroissance des gains. Il refait ensuite à la main l'évaluateur sur la question des frais à Dubaï, joue les six scénarios de l'agent en vérifiant pour chacun la suite des outils, les verdicts et le contenu de la réponse, et termine en montrant que la boucle canonique arrête un repli répété et que deux couples de seuils incohérents lèvent `ValueError`. La dernière ligne n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 30 sexies — Corrective RAG et Agentic RAG : évaluateur de récupération, raffinage, repli web, budget, boucle canonique."""
import json
import math
import random
import re
import sys
import unicodedata
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM et boucle d'agent (code canonique)
@dataclass
class Bloc:
    type: str                      # "text" ou "tool_use"
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class Reponse:
    stop_reason: str               # "end_turn", "tool_use", "max_tokens", "refusal", "pause_turn"
    content: list


def texte(t: str) -> Bloc:
    return Bloc(type="text", text=t)


def appel_outil(nom: str, arguments: dict, id_: str) -> Bloc:
    return Bloc(type="tool_use", id=id_, name=nom, input=arguments)


class FakeLLM:
    """Faux LLM scripté : renvoie les réponses prévues, dans l'ordre. Déterministe, gratuit."""

    def __init__(self, script: list):
        self.script = list(script)
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        if self.appels >= len(self.script):
            raise RuntimeError("script épuisé : le faux LLM n'a plus de réponse prévue")
        reponse = self.script[self.appels]
        self.appels += 1
        return reponse


def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    """Boucle percevoir → décider → agir → observer, avec trois arrêts."""
    messages = [{"role": "user", "content": question}]
    trace = []
    precedente = None
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        messages.append({"role": "assistant", "content": reponse.content})   # tel quel, sans retouche
        if reponse.stop_reason == "refusal":
            return {"statut": "refus", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "max_tokens":
            return {"statut": "tronque", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "pause_turn":
            continue
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if reponse.stop_reason == "end_turn" or not appels:
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape}
        signature = [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]
        if signature == precedente:           # même action, mêmes arguments, deux fois de suite
            return {"statut": "boucle", "trace": trace, "etapes": etape}
        precedente = signature
        resultats = []
        for b in appels:
            try:
                sortie = outils[b.name](**b.input)
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": json.dumps(sortie, ensure_ascii=False)})
                trace.append((b.name, b.input, sortie))
            except Exception as e:            # l'erreur repart vers le modèle, elle n'est pas avalée
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": f"{type(e).__name__}: {e}", "is_error": True})
                trace.append((b.name, b.input, f"ERREUR {e}"))
        messages.append({"role": "user", "content": resultats})   # tous les résultats dans UN message
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes}


# ---------------------------------------------------------------- recherche lexicale (code canonique, étape 22)
def idf_bm25(n_t: int, n_docs: int) -> float:
    """Variante utilisée par Lucene et la plupart des moteurs : toujours positive."""
    return math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))


def bm25_score(requete: list[str], doc: list[str], corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> float:
    n_docs = len(corpus)
    avgdl = sum(len(d) for d in corpus) / n_docs
    score = 0.0
    for t in requete:
        f = doc.count(t)
        if f == 0:
            continue
        n_t = sum(1 for d in corpus if t in d)
        score += idf_bm25(n_t, n_docs) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc) / avgdl))
    return score


# ---------------------------------------------------------------- probabilités et coût du repli (démonstration)
def p_juste(g: float, a: float, s: float, f: float, w: float) -> float:
    """P(juste) = g [(1 − f) a + f w] + (1 − g) s w : une mauvaise récupération non détectée donne une réponse fausse."""
    for v in (g, a, s, f, w):
        if not 0.0 <= v <= 1.0:
            raise ValueError("toutes les probabilités doivent être dans [0, 1]")
    return g * ((1 - f) * a + f * w) + (1 - g) * s * w


def cout_attendu(g: float, s: float, f: float, c1: float, c2: float, c3: float) -> float:
    """E[coût] = c1 + c2 + P(repli) c3, avec P(repli) = g f + (1 − g) s."""
    return c1 + c2 + (g * f + (1 - g) * s) * c3


def p_juste_budget(g: float, w: float, budget: int) -> float:
    """Évaluateur parfait, B replis indépendants au plus : g + (1 − g)(1 − (1 − w)^B)."""
    return g + (1 - g) * (1 - (1 - w) ** budget)


def replis_attendus(g: float, w: float, budget: int) -> float:
    """Nombre moyen d'appels de repli : (1 − g)(1 − (1 − w)^B) / w (série géométrique, étape 11)."""
    return (1 - g) * (1 - (1 - w) ** budget) / w


def simuler(n: int, g: float, a: float, s: float, f: float, w: float, budget: int, rng: random.Random):
    """Tire n questions et applique la politique : détecter, puis replier au plus « budget » fois."""
    justes, replis = 0, 0
    for _ in range(n):
        bonne = rng.random() < g
        alerte = rng.random() < (f if bonne else s)
        if not alerte:
            justes += bonne and rng.random() < a
            continue
        for _ in range(budget):
            replis += 1
            if rng.random() < w:
                justes += 1
                break
    return justes / n, replis / n


# ---------------------------------------------------------------- texte, évaluateur de récupération, raffinage
MOTS_VIDES = {"a", "au", "aux", "ce", "comment", "d", "dans", "de", "des", "du", "en", "entre", "est", "et", "il",
              "l", "la", "le", "les", "lors", "mon", "ne", "non", "ou", "par", "pour", "quel", "quelle", "quels",
              "qu", "que", "qui", "s", "se", "son", "sur", "t", "un", "une"}
ENTITES = {"dubai", "abu", "dhabi", "sharjah", "ajman", "fujairah", "difc", "adgm"}   # émirats et zones franches
TAU_HAUT, TAU_BAS, TAU_PHRASE = 0.6, 0.3, 0.3          # seuils illustratifs, à calibrer sur un jeu étiqueté
COUTS = {"chercher_base": 1.0, "chercher_web": 3.0, "demander_precision": 0.5}   # unités illustratives


def termes(t: str) -> list[str]:
    """Minuscules, accents retirés, mots vides retirés, pluriel en « s » retiré (racinisation grossière)."""
    t = "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))
    mots = [m for m in re.findall(r"[a-z0-9]+", t) if m not in MOTS_VIDES]
    return [m[:-1] if len(m) > 3 and m.endswith("s") else m for m in mots]


def couverture(question: str, passage: str) -> float:
    """Score de l'évaluateur, dans [0, 1] : part des termes distincts de la question présents dans le passage,
    ramenée à 0 si la question nomme une entité (émirat, zone franche) que le passage ne nomme pas."""
    q = set(termes(question))
    if not q:
        raise ValueError("question vide après normalisation")
    p = set(termes(passage))
    if (q & ENTITES) - p:
        return 0.0
    return len(q & p) / len(q)


def verdict(score_max: float, tau_haut: float = TAU_HAUT, tau_bas: float = TAU_BAS) -> str:
    """Trois zones de CRAG : correct si un passage atteint τ_haut, incorrect si tous restent sous τ_bas."""
    if not 0.0 <= tau_bas <= tau_haut <= 1.0:
        raise ValueError("il faut 0 <= tau_bas <= tau_haut <= 1")
    if score_max >= tau_haut:
        return "correct"
    if score_max < tau_bas:
        return "incorrect"
    return "ambigu"


def phrases(t: str) -> list[str]:
    return [p for p in re.split(r"(?<=[.!?])\s+", t.strip()) if p]


def raffiner(question: str, passages: list[dict], tau_phrase: float = TAU_PHRASE) -> list[dict]:
    """Décomposer puis recomposer : on ne garde que les phrases assez couvrantes, avec leur source."""
    return [{"id": p["id"], "texte": ph} for p in passages for ph in phrases(p["texte"])
            if couverture(question, ph) >= tau_phrase]


@dataclass
class Source:
    id: str
    texte: str
    origine: str = "base"          # "base" (documents internes) ou "web" (recherche simulée)


def rechercher(corpus: list[Source], requete: str, k: int) -> list[Source]:
    """BM25 (étape 22) ; seuls les documents qui contiennent un terme de la requête sont classés."""
    docs = [termes(s.texte) for s in corpus]
    q = termes(requete)
    scores = [(bm25_score(q, d, docs), s.id, s) for d, s in zip(docs, corpus)]
    return [s for sc, _, s in sorted(scores, key=lambda x: (-x[0], x[1])) if sc > 0][:k]


def evaluer_et_raffiner(question: str, trouves: list[Source], tau_haut: float, tau_bas: float) -> dict:
    passages = [{"id": f"{s.origine}:{s.id}", "texte": s.texte, "score": round(couverture(question, s.texte), 3)}
                for s in trouves]
    score_max = max((p["score"] for p in passages), default=0.0)
    v = verdict(score_max, tau_haut, tau_bas)
    retenus = [] if v == "incorrect" else raffiner(question, passages)
    return {"verdict": v, "score_max": score_max, "passages": passages, "retenus": retenus}


BASE = [
    Source("immo-01", "Frais de transfert : le DLD prélève 4 % de la valeur du bien lors de chaque vente à Dubaï. "
                      "Le paiement intervient au moment du transfert de propriété."),
    Source("immo-02", "Un contrat de location résidentielle à Dubaï s'enregistre auprès d'Ejari."),
    Source("banque-01", "Le ratio d'endettement total ne doit pas dépasser 50 % du revenu régulier, 30 % pour un retraité."),
    Source("banque-02", "Un prêt personnel ne dépasse pas 20 fois le salaire mensuel, sur 48 mois au plus."),
    Source("fisc-01", "TVA : le taux standard est de 5 % ; le loyer résidentiel est exonéré."),
    Source("fisc-02", "Impôt sur les sociétés : 9 % au-delà de 375 000 AED de bénéfice imposable."),
    Source("rh-01", "Indemnité de fin de service du secteur privé (décret-loi fédéral 33/2021) : 21 jours de salaire "
                    "de base par année les cinq premières années, 30 jours au-delà."),
    Source("rh-02", "Les salariés du DIFC relèvent d'un régime d'épargne propre, DEWS, et non de l'indemnité fédérale."),
]
WEB = [
    Source("web-01", "Le dirham des Émirats (AED) est indexé sur le dollar américain : 1 USD = 3,6725 AED, taux de change fixe.", "web"),
    Source("web-02", "DIFC : le régime DEWS remplace l'indemnité de fin de service ; il repose sur des versements "
                     "de l'employeur (page simulée).", "web"),
    Source("web-03", "Forum : quelqu'un connaît les frais du DLD ? Je crois que c'est 2 %, pas sûr.", "web"),
    Source("web-04", "Abu Dhabi : les plus belles plages et les musées à visiter (guide touristique).", "web"),
]


# ---------------------------------------------------------------- outils de l'agent et faux LLM à règles
def fabriquer_outils(reponses_utilisateur: list[str], budget_web: int, tau_haut: float, tau_bas: float) -> dict:
    """Trois outils ; le budget de recherche web est tenu DANS l'outil, qui refuse au-delà (on ne retire pas l'outil)."""
    etat = {"web": 0}

    def chercher_base(requete: str) -> dict:
        return evaluer_et_raffiner(requete, rechercher(BASE, requete, 3), tau_haut, tau_bas)

    def chercher_web(requete: str) -> dict:
        if etat["web"] >= budget_web:
            return {"refus": "budget de recherche web épuisé"}
        etat["web"] += 1
        return evaluer_et_raffiner(requete, rechercher(WEB, requete, 2), tau_haut, tau_bas)

    def demander_precision(question: str) -> dict:
        return {"reponse_utilisateur": reponses_utilisateur.pop(0) if reponses_utilisateur else ""}

    return {"chercher_base": chercher_base, "chercher_web": chercher_web, "demander_precision": demander_precision}


ABSTENTION = "Je n'ai pas de source assez fiable pour répondre ; je transmets la question à un conseiller."


class LLMRegles:
    """Faux LLM déterministe : il lit l'historique et choisit l'action suivante, comme un modèle guidé par son prompt."""

    def __init__(self):
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        self.appels += 1
        question = messages[0]["content"]
        faits = [b for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "tool_use"]
        sorties = [json.loads(r["content"]) for m in messages[1:] if m["role"] == "user"
                   for r in m["content"] if not r.get("is_error")]
        nid = f"t{len(faits) + 1}"
        if not faits:
            immobilier = any(m in termes(question) for m in ("frai", "bail", "location"))
            if immobilier and not set(termes(question)) & ENTITES:
                return Reponse("tool_use", [appel_outil("demander_precision", {"question": "Dans quel émirat se trouve le bien ?"}, nid)])
            return Reponse("tool_use", [appel_outil("chercher_base", {"requete": question}, nid)])
        dernier, sortie = faits[-1], sorties[-1]
        if dernier.name == "demander_precision":
            requete = question + " " + sortie["reponse_utilisateur"]
            return Reponse("tool_use", [appel_outil("chercher_base", {"requete": requete}, nid)])
        if dernier.name == "chercher_base" and sortie["verdict"] != "correct":
            return Reponse("tool_use", [appel_outil("chercher_web", {"requete": dernier.input["requete"]}, nid)])
        if "refus" in sortie:
            return Reponse("end_turn", [texte(ABSTENTION)])
        bonnes = [s for s in sorties if s.get("verdict") == "correct"]
        if not bonnes:
            web_faits = [b for b in faits if b.name == "chercher_web"]
            if len(web_faits) == 1:                          # une seule reformulation : les termes clés seulement
                courte = " ".join(termes(web_faits[0].input["requete"]))
                return Reponse("tool_use", [appel_outil("chercher_web", {"requete": courte}, nid)])
            return Reponse("end_turn", [texte(ABSTENTION)])
        cites = [r for s in sorties if s.get("verdict") in ("correct", "ambigu") for r in s["retenus"]]
        return Reponse("end_turn", [texte(" ".join(f"{r['texte']} [{r['id']}]" for r in cites))])


def lancer(question: str, reponses_utilisateur: list[str] | None = None, budget_web: int = 1,
           tau_haut: float = TAU_HAUT, tau_bas: float = TAU_BAS) -> dict:
    outils = fabriquer_outils(list(reponses_utilisateur or []), budget_web, tau_haut, tau_bas)
    r = executer_agent(LLMRegles(), "Agent RAG correctif : cite tes sources, abstiens-toi sans source fiable.",
                       question, outils, [], max_etapes=6)
    r["cout"] = sum(0.0 if isinstance(s, dict) and "refus" in s else COUTS[nom] for nom, _, s in r["trace"])
    r["verdicts"] = [s.get("verdict", s.get("refus", "précision")) if isinstance(s, dict) else s
                     for _, _, s in r["trace"]]
    return r


def main() -> None:
    print("1. Probabilité de réponse juste et coût (g = 0.8, a = 1, s = 0.9, f = 0.1, w = 0.7)")
    p0 = 0.8 * 1.0
    p1 = p_juste(0.8, 1.0, 0.9, 0.1, 0.7)
    p_parfait = p_juste(0.8, 1.0, 1.0, 0.0, 0.7)
    c1 = cout_attendu(0.8, 0.9, 0.1, 1.0, 0.2, 3.0)
    print(f"  RAG simple {p0:.3f} ; CRAG {p1:.3f} ; CRAG à évaluateur parfait {p_parfait:.3f} = 0.8 + 0.2 × 0.7")
    print(f"  P(repli) = 0.8 × 0.1 + 0.2 × 0.9 = {0.8 * 0.1 + 0.2 * 0.9:.2f} ; coût attendu {c1:.2f} contre 1.00")
    assert round(p1, 3) == 0.902 and round(p_parfait, 3) == 0.94 and round(c1, 2) == 1.98
    sim, _ = simuler(60000, 0.8, 1.0, 0.9, 0.1, 0.7, 1, random.Random(7))
    print(f"  simulation de 60 000 questions : P(juste) = {sim:.4f}")
    assert abs(sim - p1) < 0.01
    fausse_alarme = p_juste(0.8, 1.0, 0.9, 0.6, 0.7)
    print(f"  évaluateur trop sévère (f = 0.6) : {fausse_alarme:.3f} < {p0:.3f} : le repli dégrade la réponse")
    assert fausse_alarme < p0

    print("2. Budget de replis (évaluateur parfait, replis indépendants)")
    for B in (1, 2, 3):
        pb, nb = p_juste_budget(0.8, 0.7, B), replis_attendus(0.8, 0.7, B)
        sim_p, sim_n = simuler(60000, 0.8, 1.0, 1.0, 0.0, 0.7, B, random.Random(B))
        print(f"  B = {B} : P(juste) = {pb:.4f} (simulé {sim_p:.4f}) ; replis moyens = {nb:.4f} (simulé {sim_n:.4f})")
        assert abs(sim_p - pb) < 0.01 and abs(sim_n - nb) < 0.01
    assert round(p_juste_budget(0.8, 0.7, 3), 4) == 0.9946 and round(replis_attendus(0.8, 0.7, 3), 3) == 0.278
    gains = [p_juste_budget(0.8, 0.7, B + 1) - p_juste_budget(0.8, 0.7, B) for B in range(4)]
    assert all(g2 < g1 for g1, g2 in zip(gains, gains[1:]))          # rendements décroissants

    print("3. Évaluateur de récupération à la main")
    q = "Quels frais de transfert le DLD prélève-t-il sur la vente d'un bien à Dubaï Marina ?"
    print(f"  termes : {termes(q)}")
    sc = [couverture(q, ph) for ph in phrases(BASE[0].texte)]
    print(f"  couverture des deux phrases de immo-01 : {sc[0]:.3f} et {sc[1]:.3f} ; verdict {verdict(max(sc))}"
          f" (τ_haut = 0.6), {verdict(max(sc), 0.9)} (τ_haut = 0.9)")
    assert termes(q) == ["frai", "transfert", "dld", "preleve", "vente", "bien", "dubai", "marina"]
    assert (sc[0], sc[1]) == (0.875, 0.0) and verdict(0.875) == "correct" and verdict(0.875, 0.9) == "ambigu"

    print("4. Scénarios de l'agent (boucle canonique, faux LLM à règles)")
    scenarios = [
        ("correct", q, [], {}),
        ("incorrect → web", "Quel est le taux de change fixe entre le dirham et le dollar américain ?", [], {}),
        ("ambigu → base + web", "Comment calculer l'indemnité de fin de service d'un salarié du DIFC ?", [], {}),
        ("précision puis abstention", "Quels frais de transfert pour mon appartement ?", ["Abu Dhabi"], {}),
        ("rien nulle part", "Quel est le prix d'un permis de pêche à Fujaïrah ?", [], {"budget_web": 2}),
        ("seuil trop sévère", q, [], {"tau_haut": 0.9}),
    ]
    resultats = {}
    for nom, question, utilisateur, reglages in scenarios:
        r = lancer(question, utilisateur, **reglages)
        resultats[nom] = r
        outils = " → ".join(n for n, _, _ in r["trace"])
        print(f"  [{nom}] {outils} | verdicts : {' → '.join(r['verdicts'])} | coût {r['cout']:.1f}")
        print(f"      {r['reponse']}")
    attendu = {
        "correct": (["chercher_base"], ["correct"]),
        "incorrect → web": (["chercher_base", "chercher_web"], ["incorrect", "correct"]),
        "ambigu → base + web": (["chercher_base", "chercher_web"], ["ambigu", "correct"]),
        "précision puis abstention": (["demander_precision", "chercher_base", "chercher_web", "chercher_web"],
                                      ["précision", "incorrect", "ambigu", "budget de recherche web épuisé"]),
        "rien nulle part": (["chercher_base", "chercher_web", "chercher_web"], ["incorrect", "incorrect", "incorrect"]),
        "seuil trop sévère": (["chercher_base", "chercher_web", "chercher_web"],
                              ["ambigu", "incorrect", "budget de recherche web épuisé"]),
    }
    for nom, (outils, verdicts) in attendu.items():
        r = resultats[nom]
        assert r["statut"] == "fini" and [n for n, _, _ in r["trace"]] == outils and r["verdicts"] == verdicts, nom
    assert "4 %" in resultats["correct"]["reponse"] and "paiement" not in resultats["correct"]["reponse"]
    assert "3,6725" in resultats["incorrect → web"]["reponse"]
    rep = resultats["ambigu → base + web"]["reponse"]
    assert "[base:rh-02]" in rep and "[web:web-02]" in rep and "rh-01" not in rep    # la règle fédérale est écartée
    for nom in ("précision puis abstention", "rien nulle part", "seuil trop sévère"):
        assert resultats[nom]["reponse"] == ABSTENTION
    assert "4 %" not in resultats["précision puis abstention"]["reponse"]          # pas la règle de Dubaï pour Abu Dhabi
    assert resultats["seuil trop sévère"]["cout"] > resultats["correct"]["cout"]

    print("5. La boucle canonique arrête un repli répété à l'identique")
    meme = appel_outil("chercher_web", {"requete": "permis peche fujairah"}, "t1")
    outils = fabriquer_outils([], 5, TAU_HAUT, TAU_BAS)
    r = executer_agent(FakeLLM([Reponse("tool_use", [meme]), Reponse("tool_use", [meme])]), "s", "q", outils, [])
    print(f"  statut {r['statut']} après {r['etapes']} étapes et {len(r['trace'])} appel exécuté")
    assert r["statut"] == "boucle" and len(r["trace"]) == 1

    for mauvais in ((0.5, 0.6), (0.6, -0.1)):
        try:
            verdict(0.5, *mauvais)
        except ValueError:
            pass
        else:
            raise AssertionError("des seuils incohérents auraient dû être refusés")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Probabilité de réponse juste et coût (g = 0.8, a = 1, s = 0.9, f = 0.1, w = 0.7)
  RAG simple 0.800 ; CRAG 0.902 ; CRAG à évaluateur parfait 0.940 = 0.8 + 0.2 × 0.7
  P(repli) = 0.8 × 0.1 + 0.2 × 0.9 = 0.26 ; coût attendu 1.98 contre 1.00
  simulation de 60 000 questions : P(juste) = 0.9023
  évaluateur trop sévère (f = 0.6) : 0.782 < 0.800 : le repli dégrade la réponse
…
  B = 3 : P(juste) = 0.9946 (simulé 0.9951) ; replis moyens = 0.2780 (simulé 0.2787)
…
  couverture des deux phrases de immo-01 : 0.875 et 0.000 ; verdict correct (τ_haut = 0.6), ambigu (τ_haut = 0.9)
4. Scénarios de l'agent (boucle canonique, faux LLM à règles)
  [correct] chercher_base | verdicts : correct | coût 1.0
  [incorrect → web] chercher_base → chercher_web | verdicts : incorrect → correct | coût 4.0
  [ambigu → base + web] chercher_base → chercher_web | verdicts : ambigu → correct | coût 4.0
  [précision puis abstention] demander_precision → chercher_base → chercher_web → chercher_web | verdicts : précision → incorrect → ambigu → budget de recherche web épuisé | coût 4.5
  [rien nulle part] chercher_base → chercher_web → chercher_web | verdicts : incorrect → incorrect → incorrect | coût 7.0
  [seuil trop sévère] chercher_base → chercher_web → chercher_web | verdicts : ambigu → incorrect → budget de recherche web épuisé | coût 4.0
      Je n'ai pas de source assez fiable pour répondre ; je transmets la question à un conseiller.
  statut boucle après 2 étapes et 1 appel exécuté
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : corriger un RAG, c'est trois fonctions et une politique. Le verdict de l'évaluateur décide de la suite, le budget et la règle anti-répétition bornent le coût, et l'abstention est une issue normale quand aucune source n'atteint le seuil. Les formules disent à l'avance ce que la correction rapporte et ce qu'elle coûte.

### Brancher un vrai modèle

La boucle ne change pas : on remplace `LLMRegles()` par l'adaptateur `ClaudeLLM` du parcours et l'on décrit les trois outils au format de l'API. Le modèle choisit alors lui-même ses appels, et c'est le prompt système qui porte la politique : chercher d'abord dans la base, ne répondre qu'avec des sources jugées correctes, sinon s'abstenir. En production, `demander_precision` ne bloque pas la boucle : il termine le tour en posant la question à l'utilisateur, et la réponse de celui-ci ouvre le tour suivant.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`schema(nom, description, champ)`** — Cette fonction est le rédacteur de fiches techniques qui décrit chaque outil au modèle dans le format que l'API attend : elle reçoit le nom de l'outil, une phrase de description et le nom de son unique argument, et renvoie un dictionnaire avec ce nom, cette description, l'option `strict` activée et un schéma d'entrée qui déclare un objet à un seul champ de type chaîne, obligatoire, sans aucune propriété supplémentaire. Elle sert à construire la liste `SCHEMAS` des trois outils, `chercher_base`, `chercher_web` et `demander_precision` ; l'extrait n'est pas exécuté par le harnais.

```python
# [extrait] — schémas des trois outils pour l'adaptateur Claude du parcours (non exécuté par le harnais)
def schema(nom: str, description: str, champ: str) -> dict:
    return {"name": nom, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": {champ: {"type": "string"}},
                             "required": [champ], "additionalProperties": False}}


SCHEMAS = [
    schema("chercher_base", "Cherche dans les documents internes. Renvoie un verdict (correct, ambigu, incorrect) "
                            "et les phrases retenues avec leur source.", "requete"),
    schema("chercher_web", "Cherche dans les sources externes autorisées, dans la limite du budget. Même format de sortie.", "requete"),
    schema("demander_precision", "Pose une question courte à l'utilisateur quand une information manque.", "question"),
]
# resultat = executer_agent(ClaudeLLM(), system, question, fabriquer_outils([], 1, 0.6, 0.3), SCHEMAS)
```

## Squelette algorithmique

Deux algorithmes. Le premier est l'outil correctif : il prend une requête et un corpus et renvoie un verdict et des phrases sourcées. Le second est la politique de l'agent : il enchaîne les outils jusqu'à une réponse ou une abstention, dans les limites du budget.

```text
ALGORITHME OutilCorrectif
ENTRÉES : requête q, corpus, k, seuils τ⁺ ≥ τ⁻, seuil de phrase τp
SORTIE  : verdict, phrases retenues (avec leur source)

  D ← les k documents de meilleur score BM25 (score > 0)
  POUR CHAQUE d DE D FAIRE
      SI une entité nommée par q manque à d ALORS φ(d) ← 0
      SINON φ(d) ← |termes(q) ∩ termes(d)| / |termes(q)|
  FIN POUR
  m ← max des φ(d) (0 si D est vide)
  SI m ≥ τ⁺ ALORS verdict ← « correct »
  SINON SI m < τ⁻ ALORS verdict ← « incorrect »
  SINON verdict ← « ambigu »
  SI verdict = « incorrect » ALORS retenues ← vide
  SINON retenues ← les phrases u des documents de D telles que φ(u) ≥ τp
  RETOURNER verdict, retenues
```

**Complexité.** BM25 coûte O(N × L) sur N documents de longueur L avec le calcul simple de l'étape 22 ; l'évaluation coûte O(k × L) avec des ensembles de termes, et le raffinage aussi, puisque chaque phrase n'est lue qu'une fois. La mémoire est en O(k × L). Avec un évaluateur neuronal, le coût est dominé par ses k passages d'inférence, comme pour le cross-encodeur de l'étape 30 bis.

**Du squelette au code.** La première ligne est `rechercher`, la boucle de score `couverture` (avec la règle d'entité), le choix des trois zones `verdict`, la dernière partie `raffiner` avec `phrases`, et l'ensemble `evaluer_et_raffiner`. Les outils `chercher_base` et `chercher_web` l'appellent sur leur corpus.

```text
ALGORITHME AgentRAGCorrectif
ENTRÉES : question, budget de replis B, plafond d'étapes
SORTIE  : réponse citée, ou abstention

  SI la question demande une information manquante (par exemple l'émirat) ALORS
      précision ← DemanderPrécision ; question ← question + précision
  résultat ← OutilCorrectif(question, base)
  SI résultat.verdict = « correct » ALORS RETOURNER les phrases retenues, citées
  essais ← 0 ; requête ← question
  TANT QUE essais < B FAIRE
      essais ← essais + 1
      externe ← OutilCorrectif(requête, sources externes)       (l'outil refuse au-delà du budget)
      SI externe.verdict = « correct » ALORS
          RETOURNER les phrases retenues de la base (si ambiguë) et de l'externe, citées
      requête ← termes clés de la question                        (on reformule, jamais à l'identique)
  FIN TANT QUE
  RETOURNER abstention et transfert à un humain
```

**Complexité.** Au plus 2 + B appels d'outils par question, plus une précision éventuelle, et au plus `max_etapes` appels au modèle. Le coût moyen vaut c₁ + c₂ + P(alerte) × c₃ pour un seul repli (point 3), et le nombre moyen de replis est borné par (1 − g)/w (point 4). La mémoire est celle de l'historique des messages, qui croît avec le nombre d'étapes, d'où le plafond.

**Du squelette au code.** La politique est `LLMRegles.create`, qui relit l'historique à chaque tour. La boucle est `executer_agent`, avec son arrêt sur répétition et `max_etapes`. Le budget est le compteur `etat["web"]` de `chercher_web`, et `lancer` assemble le tout et compte les coûts.

## Cas d'usage réels aux Émirats

Les probabilités, les seuils, les coûts et les volumes ci-dessous sont illustratifs ; chaque équipe les mesure sur un jeu de questions étiquetées de son métier.

### Banque — une circulaire que la base interne n'a pas encore

L'assistant de conformité d'une banque de détail de Dubaï répond aux conseillers à partir de la politique de crédit interne, qui transpose les règles de la CBUAE (endettement total d'au plus 50 % du revenu, 30 % pour un retraité ; prêt personnel d'au plus 20 fois le salaire et 48 mois). Quand une question porte sur une circulaire récente que l'équipe de conformité n'a pas encore intégrée, la recherche interne ramène des passages voisins mais pas la règle : l'évaluateur rend « incorrect » ou « ambigu ». Le repli ne va pas sur le web ouvert. Il interroge une liste blanche de publications officielles, téléchargées et horodatées par l'équipe, ce qui élève w et retire le risque de sources douteuses. Sur 300 questions étiquetées, l'équipe mesure par exemple g = 0,85, a = 0,97, s = 0,92, f = 0,08 et w = 0,8 : la formule du point 1 donne 0,923 contre 0,8245 sans correction, pour 0,206 repli par question, et f* vaut 0,764, si bien que les fausses alarmes sont loin d'être nuisibles. Sans évaluateur, l'agent citerait avec assurance une version périmée de la règle, et le conseiller monterait un dossier non conforme. Quand rien n'atteint τ⁺, l'agent s'abstient et transmet à un responsable de la conformité. On suit la part de réponses citant une source datée de moins de trois mois et le taux d'abstention.

### RH — le régime du DIFC n'est pas la règle fédérale

Un cabinet RH présent dans plusieurs émirats répond aux salariés de ses entreprises clientes. La question « Comment calculer l'indemnité de fin de service d'un salarié du DIFC ? » est le scénario 3 du programme. La règle fédérale du décret-loi 33/2021 (21 jours par année les cinq premières années, 30 jours au-delà, plafond de 24 mois) couvre autant de mots de la question que la bonne règle, mais elle ne nomme pas le DIFC : la contrainte d'entité la ramène à 0 et le raffinage l'écarte. Le verdict de la base est ambigu (0,5), et le repli trouve la page sur DEWS (0,667). La réponse cite les deux sources et renvoie au régime d'épargne du DIFC, sans appliquer la formule fédérale. Sans cette correction, l'agent aurait produit un montant d'indemnité chiffré et faux, puisque le salarié relève d'un autre régime : c'est le mode d'échec que l'étape 26 décrivait déjà au niveau du classement. Les ressortissants émiriens relèvent quant à eux de la GPSSA : une règle d'entité du même type, sur la nationalité du salarié, écarte pour eux aussi la formule fédérale. Toute réponse reste à confirmer avec le texte en vigueur avant un versement. On suit la part des réponses dont le régime cité correspond au régime réel du salarié, contrôlée sur un échantillon chaque mois.

### Immobilier — demander l'émirat plutôt que deviner

Une agence immobilière de Dubaï et d'Abu Dhabi reçoit « Quels frais de transfert pour mon appartement ? », le scénario 4. Les frais de transfert du DLD, 4 % de la valeur du bien, sont propres à Dubaï : appliquer ce taux à Abu Dhabi serait une erreur chiffrée. L'agent demande donc l'émirat avant de chercher, pour un coût de 0,5 unité, puis cherche « … Abu Dhabi ». Le seul document interne sur les frais ne nomme pas Abu Dhabi : score 0, verdict incorrect. Le web simulé ne ramène qu'un guide touristique (0,4, ambigu), et la reformulation est refusée par le budget. L'agent s'abstient et transmet à un conseiller de l'agence d'Abu Dhabi, pour un coût total de 4,5 unités. L'erreur évitée est concrète : pour un appartement de 1,5 million d'AED, 4 % représentent 60 000 AED annoncés à tort. L'équipe enrichit ensuite sa base avec le barème d'Abu Dhabi validé par son service juridique, ce qui fera passer cette question en « correct ». On suit le taux d'abstention par émirat, qui signale les trous de la base, et la part des précisions demandées qui ont changé la réponse.

### Assurance — choisir τ⁺ avec la formule, pas au jugé

L'assistant des gestionnaires d'un assureur auto et santé cherche dans les conditions générales ; son repli consiste à interroger le gestionnaire de sinistres expert, ce qui coûte cher et répond moins vite. L'équipe mesure g = 0,9, a = 0,95, s = 0,8 et w = 0,6 sur un jeu étiqueté. La formule du point 2 donne f* = 0,1 × 0,8 × 0,6 / (0,9 × 0,35) ≈ 0,152 : au-delà de 15 % de fausses alarmes, la correction fait plus de mal que de bien. Avec un τ⁺ qui donne f = 0,1, la justesse vaut 0,8715 contre 0,855 sans correction. Un collègue propose un seuil plus sévère, « par prudence », qui monte f à 0,25 : la justesse tombe à 0,824, sous le RAG simple, parce que l'on remplace trop de bonnes réponses par l'avis plus lent et moins sûr du repli. L'équipe trace donc s et f en fonction de τ⁺ sur son jeu étiqueté (point 5) et retient le plus grand τ⁺ qui garde f sous 0,1. L'assurance est supervisée par la CBUAE, et toute décision sur un sinistre reste celle du gestionnaire. On suit s et f chaque mois, recalculés sur les dossiers relus.

### Crypto — un budget de replis tenu par la latence

L'agent d'assistance d'une plateforme d'actifs virtuels agréée par la VARA répond aux clients sur les frais, les limites de retrait et les délais. Quand la base interne ne suffit pas, il consulte les pages publiques de la plateforme, plus à jour mais plus lentes à interroger. Avec g = 0,75 et w = 0,6, la formule du point 4 donne une justesse de 0,9, 0,96 et 0,984 pour B = 1, 2 et 3, pour 0,25, 0,35 et 0,39 repli en moyenne par question. Le troisième repli ne rapporte que 2,4 points, et il ajoute dans le pire cas un aller-retour de plus à une conversation où le client attend. L'équipe fixe donc B = 2, tenu dans l'outil, et la politique reformule entre les deux essais pour ne pas répéter un échec corrélé ; la boucle canonique arrête d'elle-même un appel identique. Les règles de communication aux clients d'une plateforme agréée imposent de ne citer que les conditions en vigueur (à confirmer avec le règlement de la VARA) : une page datée, plus ancienne que la version interne, est jugée « ambiguë » et n'est jamais citée seule. On suit le taux de replis, la latence p95 et la part des réponses citant une version en vigueur.

### Secteur public — une précision à la fois, et rien de personnel dans la requête externe

Un service public en ligne accessible par UAE Pass répond en arabe et en anglais sur des démarches qui diffèrent selon l'émirat et le type de résident. L'agent dispose de `demander_precision`, mais l'équipe en limite l'usage à une question par tour et à l'information qui change vraiment la réponse : demander l'émirat, oui ; demander dix champs avant de chercher, non. Quand le repli vers des sources externes est nécessaire, la requête envoyée hors du périmètre ne doit contenir aucune donnée personnelle. Un garde-fou retire donc numéro d'Emirates ID, nom et téléphone avant l'appel, parce que la PDPL encadre ce qui sort du système. Les pages ramenées sont traitées comme des données et jamais comme des instructions : une page qui contiendrait « ignore tes consignes » est une injection indirecte (étape 4), que l'évaluateur ne doit pas récompenser. Quand rien n'atteint τ⁺, l'agent oriente l'usager vers un agent humain dans sa langue, au lieu d'improviser une procédure. On suit la part de demandes résolues sans humain, le nombre moyen de précisions par conversation et le nombre de requêtes externes bloquées par le filtre de données personnelles.

## Pièges et limites

- **Faire confiance à un évaluateur lexical.** Il se laisse tromper par les synonymes et par les négations : rh-02 contient « indemnité fédérale » précisément pour dire qu'elle ne s'applique pas. On mesure s et f sur un jeu étiqueté, puis on passe à un cross-encodeur (étape 30 bis) ou à un modèle juge si nécessaire.
- **Replier sur le web ouvert.** Un forum ou une page périmée font baisser w et peuvent transporter une injection indirecte (étape 4). On restreint le repli à des sources connues, on les date et on les cite.
- **Laisser sortir des données dans la requête externe.** Une recherche web est une transmission de données : on retire tout identifiant personnel avant l'appel.
- **Répéter le même repli.** Des essais identiques échouent ensemble, et la formule des essais indépendants devient fausse. On reformule, et la boucle canonique arrête la répétition.
- **Ne pas évaluer l'abstention.** Une abstention juste est un succès, une abstention sur une question que la base savait traiter est un échec coûteux (scénario « seuil trop sévère ») : on compte les deux, comme à l'étape 29.

### Exercice feuille blanche

1. Sans regarder le code, écrire `p_juste` à partir de l'arbre à quatre cas, vérifier 0,902, puis retrouver f* = 0,525 en résolvant Δ = 0.
2. Prédire, puis vérifier : avec w = 0,9 au lieu de 0,7, que vaut f* ? (Réponse : 0,2 × 0,9 × 0,9 / (0,8 × 0,1) ≈ 2,03 > 1, donc aucune valeur de f ne rend la correction nuisible.) Avec B = 4 et w = 0,7, que vaut P_B ? (Réponse : 0,8 + 0,2 × (1 − 0,3⁴) ≈ 0,9984.)
3. Trouver le bug : dans `chercher_web`, le test du budget s'écrit `if etat["web"] > budget_web:`. Que devient le scénario « précision puis abstention » ? (Réponse : la reformulation n'est plus refusée et lance une seconde vraie recherche web ; l'agent s'abstient quand même, mais pour un coût de 7,5 au lieu de 4,5.)

## Pour aller plus loin

Le Self-RAG s'entraîne en deux temps : un modèle critique annote un corpus avec les jetons de réflexion, puis le générateur apprend à les produire lui-même. À l'inférence, les probabilités de ces jetons servent à classer des segments candidats. L'Adaptive-RAG route chaque question, selon sa difficulté, vers « pas de recherche », « une recherche » ou « plusieurs étapes ». FLARE relance une recherche quand la phrase suivante contient des tokens peu probables. Le motif ReAct (Yao et al., 2022) est la forme générale de la boucle « raisonner puis agir » utilisée ici. Les frameworks d'orchestration proposent des tutoriels de CRAG prêts à l'emploi ; tout ce qu'ils font tient dans les trois fonctions et la politique de ce fichier, qu'il vaut mieux savoir réécrire. L'étape 30 septies remplace la liste de passages par un graphe de faits datés, qui permet de répondre aux questions à plusieurs sauts.

> Étape 30 sexies du parcours · Prérequis : [Index ANN : HNSW, IVF et PQ](<30e-RAG-Index-ANN-HNSW-IVF-PQ.md>) · Suite : [GraphRAG et mémoire en graphe](<30g-RAG-GraphRAG-et-Memoire-en-Graphe.md>)
