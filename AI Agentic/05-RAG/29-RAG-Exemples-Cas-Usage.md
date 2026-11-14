# Étape 29 — RAG — Exemples de RAG de bout en bout

> Étape 29 du parcours · Prérequis : [NDCG](<28-RAG-Formule-NDCG.md>) · Suite : [Applications du RAG par domaine](<30-RAG-Applications-Domaines.md>)

**Dossier :** 05-RAG  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  
**Nom du fichier :** 29-RAG-Exemples-Cas-Usage.md

## Ce que contient ce fichier

Ce fichier assemble, dans un seul programme, tout ce que les étapes 19 à 28 ont construit séparément. Il fait tourner huit questions posées à sept agents RAG jouets, un par acteur du parcours : banque, immobilier, plateforme crypto, assurance, cabinet RH, groupe de BTP et service public. Pour chaque question, l'agent appelle un outil de recherche qui classe 5 à 7 morceaux de texte avec BM25 (étape 22) et avec le cosinus (étape 19), fusionne les deux classements par RRF (étape 24) et garde les k premiers ; il répond ensuite en citant ses sources entre crochets. Un garde-fou de sortie vérifie la réponse avant de la laisser partir, et une évaluation hors ligne mesure le classement avec le Recall@k, le MRR et le NDCG. Trois éléments sont des jouets, et il faut le savoir : les vecteurs sont écrits à la main (3 à 5 axes nommés au lieu des centaines de dimensions d'un modèle d'embedding), le LLM est le faux LLM scripté du parcours, et les textes des morceaux sont fictifs, sauf les règles tirées des chiffres vérifiés du parcours (plafonds d'endettement de 50 % et 30 % et prêt personnel limité à 20 fois le salaire sur 48 mois, règles de fin de service, TVA de 5 %). Le reste — la boucle d'agent, les fonctions de score, la fusion, les métriques et le garde-fou — est du vrai code, celui qu'on garde quand on branche un vrai modèle. L'ancienne version de ce fichier donnait six exemples de deux lignes, situés en France et sans calcul ; ils sont remplacés par ces cas émiriens exécutables.

## Les mots de ce fichier, et où ils sont définis

L'ancienne version citait la Faithfulness, le Context Recall, le NDCG, le MRR et la recherche hybride sans les définir. Le tableau ci-dessous les définit en une ligne et renvoie à l'étape qui les démontre.

| Terme | Ce que c'est ici | Défini et démontré à |
|---|---|---|
| Similarité cosinus | score sémantique entre le vecteur de la question et celui d'un morceau | [étape 19](<19-RAG-Formule-Similarite-Cosinus.md>) |
| BM25 | score lexical : les mots de la question présents dans le morceau, pondérés par leur rareté et corrigés par la longueur du morceau | [étape 22](<22-RAG-Formule-BM25.md>) |
| Recherche hybride | combiner un score lexical et un score sémantique ; ici par fusion des rangs plutôt que des scores | [score hybride, étape 23](<23-RAG-Formule-Score-Hybride.md>) et [RRF, étape 24](<24-RAG-Formule-RRF.md>) |
| Recall@k | part des morceaux pertinents présents dans le top-k | [étape 25](<25-RAG-Formule-Recall-at-k.md>) |
| Precision@k | part du top-k qui est pertinente | [étape 26](<26-RAG-Formule-Precision-at-k.md>) |
| MRR | moyenne des rangs réciproques du premier morceau pertinent | [étape 27](<27-RAG-Formule-MRR.md>) |
| NDCG@k | qualité de l'ordre du top-k, avec des notes de pertinence de 0 à 3 | [étape 28](<28-RAG-Formule-NDCG.md>) |
| Faithfulness (fidélité) | part des affirmations de la réponse que les sources fournies justifient ; ici seulement **approchée** par correspondance de chaînes | [étape 54](<../10-Evaluation/54-Evaluation-Formule-Faithfulness.md>) |
| Context Recall | part de la réponse de référence que le contexte retrouvé permet de justifier ; sa variante par identifiants est exactement le Recall@k calculé ici | [étape 58](<../10-Evaluation/58-Evaluation-Formule-Context-Recall.md>) |

## La chaîne, de la question à la décision

1. **Normaliser et découper en mots.** Minuscules, accents retirés, et pour l'arabe : formes de l'alef unifiées, ta marbuta écrite comme un ha, diacritiques retirés. Les mots vides (« de », « la », « the »…) sont écartés.
2. **Classer par BM25.** Seuls les morceaux qui contiennent au moins un mot de la question entrent dans ce classement : un score nul n'est pas un rang.
3. **Classer par cosinus.** Tous les morceaux entrent dans ce classement, du plus proche au plus éloigné.
4. **Fusionner par RRF** avec

$$
k_{RRF} = 60 ,
$$

puis garder les k premiers : c'est le contexte.
5. **Construire le prompt** : une consigne, une ligne `[id] texte` par morceau, puis la question.
6. **Laisser l'agent agir** dans la boucle canonique du parcours : le faux LLM appelle l'outil `rechercher`, éventuellement un outil de calcul, puis répond en citant `[id]` ou `[outil:nom]`.
7. **Vérifier la réponse** avant de l'envoyer : trois règles, dans cet ordre (abstention, fidélité, fraîcheur des sources).
8. **Évaluer hors ligne** le classement avec les notes de pertinence connues : Recall@k, rang réciproque coupé à k (dont la moyenne est le MRR) et NDCG@k.

Le tableau sépare ce qui **classe** (fonctions de score), ce qui **décide** en ligne (seuils, sans vérité terrain) et ce qui **mesure** hors ligne (métriques d'évaluation, qui exigent des jugements de pertinence).

**Rôle :** Fonction de score lexicale · **Élément :** BM25 · **Fonction Python :** `bm25_score` · **Réglage dans ce fichier :** k₁ = 1,5 et b = 0,75

**Rôle :** Fonction de score sémantique · **Élément :** cosinus · **Fonction Python :** `cosinus` · **Réglage dans ce fichier :** vecteurs jouets à 3, 4 ou 5 axes

**Rôle :** Fusion des classements · **Élément :** RRF · **Fonction Python :** `rrf` · **Réglage dans ce fichier :** voir le bloc ci-dessous

$$
k_{RRF} = 60
$$

**Rôle :** Seuil d'abstention (en ligne) · **Élément :** meilleur cosinus du top-k · **Fonction Python :** `decider` · **Réglage dans ce fichier :** `SEUIL_COSINUS = 0.5`

**Rôle :** Seuil de fidélité (en ligne) · **Élément :** fidélité approchée de la réponse · **Fonction Python :** `fidelite_approchee`, `decider` · **Réglage dans ce fichier :** `SEUIL_FIDELITE = 1.0`, `RECOUVREMENT_MIN = 0.5`

**Rôle :** Règle de fraîcheur (en ligne) · **Élément :** une source citée est marquée « remplacée » · **Fonction Python :** `decider` · **Réglage dans ce fichier :** toute source remplacée envoie en revue humaine

**Rôle :** Métriques d'évaluation (hors ligne) · **Élément :** Recall@k, rang réciproque, NDCG@k · **Fonction Python :** `recall_at_k`, `reciprocal_rank`, `ndcg_at_k` · **Réglage dans ce fichier :** k = 3, ou k = 4 pour le cas RH

Les seuils 0,5 et 1 sont illustratifs : avec un vrai modèle d'embedding, le seuil d'abstention se calibre sur des questions hors sujet réelles, parce que les cosinus d'un modèle à l'autre n'ont pas la même échelle.

## Démonstration

### 1. Pourquoi la fusion remet le bon contrat en tête (cas BTP)

BM25 classe d'abord le modèle générique `btp-01` (score 3,4273), parce qu'il est court et contient « retenue », « garantie » et « facture », puis le contrat du lot électricité `btp-02` (2,9152), puis `btp-06` (1,8094) et `btp-04` (1,3731). Le cosinus classe `btp-02` en tête (0,9963), devant `btp-06` (0,8515) et `btp-01` (0,7987). La fusion RRF additionne les inverses des rangs décalés de 60 :

$$
\text{RRF}(\text{btp-02}) = \frac{1}{60 + 2} + \frac{1}{60 + 1} \approx 0{,}016129 + 0{,}016393 = 0{,}032522
$$

$$
\text{RRF}(\text{btp-01}) = \frac{1}{60 + 1} + \frac{1}{60 + 3} \approx 0{,}016393 + 0{,}015873 = 0{,}032266
$$

$$
\text{RRF}(\text{btp-06}) = \frac{1}{60 + 3} + \frac{1}{60 + 2} \approx 0{,}015873 + 0{,}016129 = 0{,}032002
$$

Le contrat spécifique passe devant le modèle générique **parce que** les deux scores partagent le terme 1/61 et que 1/62 > 1/63 : être deuxième et premier vaut mieux qu'être premier et troisième. Avec BM25 seul, le premier morceau pertinent est au rang 2 et le rang réciproque vaut 0,5 ; après fusion, il vaut 1. Les propriétés générales de la RRF (insensibilité à l'échelle des scores, rôle de

$$
k_{RRF}
$$

) sont démontrées à l'étape 24.

### 2. Les moyennes ne portent que sur les questions évaluables

Sept questions ont au moins un morceau pertinent. La huitième, « How do I get a fishing permit? », n'en a aucun : son Recall@k et son NDCG sont indéfinis (`None`, convention des étapes 25 et 28) et elle sort des moyennes. On obtient :

$$
\overline{\text{R@}k} = \frac{1 + 0{,}75 + 1 + 0{,}75 + 0{,}75 + 0{,}5 + 1}{7} = \frac{5{,}75}{7} \approx 0{,}8214
$$

$$
\overline{\text{NDCG@}k} = \frac{1 + 0{,}9341 + 0{,}7277 + 1 + 0{,}8722 + 0{,}9173 + 1}{7} \approx \frac{6{,}4513}{7} \approx 0{,}9216
$$

Le MRR vaut 1, parce que chaque top-1 fusionné est pertinent. Si l'on comptait 0 pour la question hors corpus au lieu de l'exclure, le rappel moyen tomberait à 5,75/8 ≈ 0,7188, une baisse qui ne dit rien du moteur : la bonne réponse à cette question était de s'abstenir, ce qu'on vérifie à part (1 abstention correcte sur 1).

### 3. Ce que la fidélité approchée garantit, et ce qu'elle ne garantit pas

La fonction `fidelite_approchee` découpe la réponse en phrases et déclare une phrase **étayée** si trois conditions sont réunies : (a) elle cite au moins une source, et toutes ses sources citées ont réellement été fournies au modèle (morceaux du top-k ou résultats d'outils) ; (b) chacun de ses nombres figure parmi les nombres de ses sources citées, « 1 450 » et « 1450 » étant considérés comme égaux ; (c) au moins la moitié de ses mots pleins figurent dans ses sources citées. Le score est la part des phrases étayées. Par construction, la condition (a) attrape toute citation inventée, et la condition (b) attrape tout nombre écrit en chiffres absent des sources citées, c'est-à-dire l'hallucination la plus coûteuse dans ces métiers (un montant, un taux, une durée) : dans le cas assurance, « 250 AED » face à une source qui dit « 500 AED » est rejeté.

Elle n'est pourtant **ni suffisante ni nécessaire**, et le programme le vérifie sur deux contre-exemples. Elle n'est pas suffisante : « Pour un client retraité, le plafond du ratio d'endettement est de 50 % du revenu régulier [banque-01][banque-02]. » obtient 1, parce que 50 figure dans `banque-01` et que tous les mots figurent dans les deux sources ; la phrase est pourtant fausse, le plafond d'un retraité étant de 30 %. Le nombre est juste, c'est son attribution qui est fausse. Elle n'est pas nécessaire : « Un retraité ne peut consacrer plus de 30 % de ses ressources au remboursement de ses crédits [banque-02]. » est une paraphrase fidèle, mais un seul de ses huit mots pleins (« retraite ») figure dans la source, et elle obtient 0. Enfin, le cas crypto montre une réponse parfaitement fidèle à sa source… qui est périmée : la fidélité ne dit rien de la validité de la source, d'où la règle de fraîcheur séparée. C'est pour ces raisons que la vraie Faithfulness de l'étape 54 extrait les affirmations de la réponse et fait juger par un modèle si chacune découle des sources.

### 4. Un résultat d'outil est une source comme une autre (cas RH)

Le montant de 55 000 AED ne figure dans aucun document : il est calculé. Si le modèle l'écrivait de lui-même, la condition (b) le rejetterait, et elle aurait raison, car rien ne prouverait le calcul. L'agent appelle donc l'outil `fin_de_service`, qui applique la fonction canonique du parcours : 5 × 21 × 10 000/30 = 35 000 AED pour les cinq premières années, plus 2 × 30 × 10 000/30 = 20 000 AED pour les deux suivantes, soit 55 000 AED, sous le plafond de 24 × 10 000 = 240 000 AED. Le résultat de l'outil, avec ses arguments, est ajouté aux sources sous l'identifiant `outil:fin_de_service`, et la phrase qui le cite est étayée. La règle générale : tout nombre calculé doit venir d'un outil et être cité comme tel.

## Le programme

### Déroulé, ligne par ligne

**Code canonique recopié.** `Bloc`, `Reponse`, `texte`, `appel_outil`, `FakeLLM` et `executer_agent` forment le port LLM et la boucle d'agent du parcours, recopiés tels quels : la même boucle tournera plus tard avec l'adaptateur Claude, sans changement. `cosinus`, `idf_bm25`, `bm25_score`, `rrf` et `gratuite_fin_de_service` sont les fonctions canoniques des étapes 19, 22 et 24 et du chapitre RH. `dedupliquer`, `recall_at_k`, `first_relevant_rank`, `reciprocal_rank`, `dcg_at_k` et `ndcg_at_k` reprennent les étapes 25 à 28, avec la même convention : `None` quand il n'y a pas de dénominateur, et un IDCG calculé sur tous les documents jugés.

**`normaliser(t)`** met en minuscules, remplace grâce au dictionnaire `ARABE` les trois formes de l'alef par l'alef nu et la ta marbuta par le ha, puis décompose le texte (`unicodedata.normalize("NFKD", ...)`) et retire les signes combinants : les accents latins (« retraité » devient « retraite ») et les diacritiques arabes. Les caractères sont écrits par leur nom Unicode (`\N{ARABIC LETTER TEH MARBUTA}`), ce qui rend le code lisible même sans clavier arabe. Le programme vérifie que l'écriture correcte de « carte d'identité émiratie » et sa variante avec ha et alef sans hamza donnent le même texte normalisé.

**`tokeniser(t, normaliser_texte)`** découpe le texte en suites de lettres et de chiffres (`[^\W_]+`, qui reconnaît aussi l'arabe) et retire les mots vides. Avec `normaliser_texte=False`, il ne fait que mettre en minuscules : c'est la version « sans normalisation » du cas secteur public.

**`nombres(t)`** renvoie l'ensemble des nombres d'un texte sous forme de flottants. Le motif accepte les milliers séparés par une espace, une espace insécable ou une fine insécable, puis retire ces espaces et remplace la virgule décimale par un point : `nombres("1 450 AED, soit 2,5 %")` vaut `{1450.0, 2.5}`.

**`Morceau`** porte l'identifiant, le texte, le vecteur jouet, la note de pertinence (la vérité terrain, de 0 à 3) et le drapeau `perime`. **`Cas`** porte le domaine, la question, son vecteur, les morceaux, k et le script du faux LLM.

**`rechercher(cas)`**.

- `bm25 = {...}` et `cos = {...}` calculent les deux scores de chaque morceau. Pour le cas BTP, BM25 donne 3,4273 à `btp-01`, 2,9152 à `btp-02`, 1,8094 à `btp-06`, 1,3731 à `btp-04` et 0 aux deux autres.
- `par_bm25 = [... if bm25[d] > 0]` ne garde que les morceaux de score positif, triés par score décroissant puis par identifiant ; l'exercice 3 montre ce qui arrive si l'on garde les scores nuls.
- `par_cos` trie tous les morceaux par cosinus décroissant.
- `fusion = [d for d, _ in rrf([par_bm25, par_cos])]` donne pour BTP `btp-02`, `btp-01`, `btp-06`… et `top` en garde les k premiers.

**`construire_prompt(question, sources)`** écrit la consigne, une ligne `[id] texte` par source, puis la question. La sortie du programme montre le prompt du cas banque.

**`fidelite_approchee(reponse, sources)`**.

- `re.split(r"(?<=[.!?])\s+", ...)` coupe après chaque point, point d'exclamation ou point d'interrogation suivi d'un blanc. La réponse du cas assurance donne deux phrases.
- `cites = re.findall(r"\[([^\]]+)\]", p)` extrait les identifiants cités ; `corps` est la phrase sans ses citations, pour que les chiffres d'un identifiant comme `assur-02` ne soient pas pris pour des nombres.
- Condition (a) : pas de citation, ou une citation absente de `sources`, et la phrase est rejetée.
- Condition (b) : `nombres(corps) <= nombres(texte_cite)` teste l'inclusion des ensembles. Pour la seconde phrase du cas assurance, `{250.0}` n'est pas inclus dans `{500.0}` : rejet.
- Condition (c) : la part des mots pleins de la phrase présents dans les sources citées doit atteindre `RECOUVREMENT_MIN`, soit 0,5.
- Le score vaut `(len(phrases) - len(non_etayees)) / len(phrases)`, soit 1/2 = 0,5 pour le cas assurance ; une réponse vide donne `None`.

**`decider(cos_max, fidelite, perimes_cites)`** applique les trois règles dans l'ordre : abstention si le meilleur cosinus du top-k est sous 0,5, revue humaine si la fidélité est sous 1 (ou indéfinie), revue humaine si une source citée est remplacée, sinon réponse.

**`executer_cas(cas)`**.

- Les deux outils sont des fonctions internes. `outil_rechercher` appelle `rechercher(cas)`, garde les classements dans `memo` pour l'évaluation, et renvoie au modèle seulement les identifiants et les textes du top-k. `outil_fin_de_service` renvoie ses arguments, l'indemnité et une phrase d'explication.
- `executer_agent(FakeLLM(cas.script), ...)` fait tourner la boucle canonique ; sa trace contient chaque appel d'outil, avec ses arguments et sa sortie.
- La boucle `for nom, _, sortie in r["trace"]` reconstruit ce que le modèle a réellement reçu : les morceaux du top-k, et pour le cas RH le JSON de `fin_de_service` sous la clé `outil:fin_de_service`.
- `cos_max` est le meilleur cosinus du top-k ; sous le seuil, la fidélité n'est pas calculée (`None`), puisque l'agent va s'abstenir.
- `perimes` liste les sources citées marquées remplacées : `["crypto-02"]` pour le cas crypto.
- Les métriques ne sont calculées que si la question a au moins un morceau pertinent ; sinon elles restent `None`.

**`script(question, reponse, *autres_outils)`** fabrique les réponses du faux LLM : un appel à `rechercher`, les appels d'outils prévus, puis la réponse finale.

**`les_cas()`** décrit les huit questions. Chaque cas indique en commentaire le sens des axes de ses vecteurs jouets.

**`main()`**, bloc par bloc.

1. Tous les cas sont exécutés, puis le prompt du cas banque est affiché et vérifié (trois lignes de sources, la question à la fin).
2. Le tableau donne, pour chaque question, le top-k fusionné, le Recall@k, le rang réciproque, le NDCG@k, la fidélité approchée, le meilleur cosinus et la décision. Le dictionnaire `attendu` vérifie toutes ces valeurs.
3. Les modes d'échec sont vérifiés un par un : la phrase rejetée du cas assurance, la source remplacée du cas crypto, les deux outils du cas RH et le morceau du DIFC entré dans son contexte, le rang réciproque de 0,5 avec BM25 seul pour le cas BTP, le score BM25 nul sans normalisation de l'arabe, l'abstention de la question hors corpus.
4. Les nombres de la démonstration sont vérifiés : les trois scores RRF du cas BTP et ses scores BM25 et cosinus, les deux contre-exemples de la fidélité approchée, les montants de fin de service, le comportement de `nombres` et de `normaliser`.
5. Les moyennes sont calculées sur les sept questions évaluables, avec les sommes 5,75 et 6,4513 de la démonstration.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fabrique joue le rôle d'un secrétaire qui glisse une phrase dans une enveloppe standard avant de l'expédier : elle reçoit une chaîne de caractères et renvoie un `Bloc` de type « text » qui la contient, sans rien vérifier ni transformer. C'est la forme sous laquelle le faux LLM rend sa réponse finale, et `script` s'en sert pour fabriquer la dernière étape de chaque scénario, celle où le modèle répond en citant ses sources entre crochets.

**`appel_outil(nom, arguments, id_)`** — Celle-ci remplit le bon de commande que le modèle adresse à un outil, comme un client qui coche une case sur un formulaire de guichet : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant d'appel, puis renvoie un `Bloc` de type « tool_use » qui porte ces trois informations. La boucle `executer_agent` lit ensuite ce bloc pour savoir quelle fonction lancer et avec quels paramètres, et l'identifiant permet de rattacher le résultat à sa demande.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui ne connaît que son texte, réplique après réplique : il reçoit la liste des réponses prévues, en garde une copie personnelle pour que le scénario d'origine ne soit jamais modifié de l'extérieur, et met à zéro le compteur `appels`, qui indiquera à chaque instant combien de répliques ont déjà été jouées. Il ne renvoie rien ; grâce à lui, chaque cas du programme tourne de façon déterministe, gratuite et identique d'une exécution à l'autre.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode imite exactement la signature d'un vrai modèle, avec ses trois arguments nommés, mais se comporte comme un souffleur qui lit simplement la réplique suivante du script, sans regarder ni la consigne, ni l'historique, ni les outils qu'on lui présente. Si toutes les répliques ont déjà été données, elle lève `RuntimeError` avec le message « script épuisé » ; sinon, elle renvoie la `Reponse` prévue et avance le compteur d'une case. C'est ce qui permet de faire tourner la boucle canonique sans appel réseau.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est le régisseur de toute la représentation, la boucle canonique du parcours qui fait alterner le modèle et les outils : il reçoit le modèle, la consigne système, la question, le dictionnaire des outils, leurs schémas et un nombre maximal d'étapes, huit par défaut. À chaque tour, il interroge le modèle, recopie sa réponse telle quelle dans l'historique, s'arrête sur un refus ou une troncature, recommence sur une pause, renvoie le texte final quand le modèle a fini ou n'appelle plus d'outil, s'arrête aussi si le modèle répète deux fois de suite la même action avec les mêmes arguments, et sinon exécute chaque outil en renvoyant les erreurs au modèle plutôt que de les avaler. Il renvoie un dictionnaire avec le statut, la trace des appels, le nombre d'étapes et, en cas de succès, la réponse.

**`cosinus(a, b)`** — C'est la boussole canonique de l'étape 19, recopiée telle quelle pour classer les morceaux par proximité de sens : la fonction reçoit deux vecteurs, lève `ValueError` si leurs dimensions diffèrent ou si l'un d'eux est nul, et renvoie le produit scalaire divisé par le produit des normes, rabattu dans [−1, 1]. Sur le cas BTP, elle donne 0,9963 à `btp-02`, 0,8515 à `btp-06` et 0,7987 à `btp-01`, et le meilleur cosinus du top-k sert ensuite au garde-fou qui décide si l'agent doit s'abstenir.

**`idf_bm25(n_t, n_docs)`** — C'est le crieur canonique de l'étape 22, qui annonce le poids d'un mot selon sa rareté dans le corpus : la fonction reçoit le nombre de morceaux qui contiennent le terme et le nombre total de morceaux, puis renvoie le logarithme de 1 + (N − n + 0,5) / (n + 0,5), une valeur toujours positive qui grandit quand le mot se fait rare. Elle n'est appelée que par `bm25_score`, pour donner plus de poids à « électricité » ou à « retraité » qu'à un mot présent partout.

**`bm25_score(requete, doc, corpus, k1, b)`** — C'est le juge lexical canonique de l'étape 22 : pour un morceau donné, il passe en revue chaque mot de la question et lui attribue des points selon sa rareté, sa fréquence dans le morceau et la longueur de celui-ci. La fonction reçoit la question et le morceau sous forme de listes de mots, le corpus entier et les réglages k1 = 1,5 et b = 0,75 par défaut, et renvoie la somme des contributions ; sur le cas BTP, elle donne 3,4273 au modèle générique `btp-01`, 2,9152 au contrat `btp-02`, 1,8094 à `btp-06` et 1,3731 à `btp-04`.

**`rrf(classements, k_rrf)`** — C'est le jury canonique de l'étape 24, qui fusionne plusieurs classements en ne regardant que les places obtenues : la fonction reçoit une liste de classements et la constante k, 60 par défaut, ajoute à chaque morceau 1 / (k + rang) pour chaque liste où il figure, et renvoie les couples (morceau, score) triés par score décroissant, les égalités départagées par le nom. Sur le cas BTP, elle place `btp-02` en tête avec 0,032522, devant `btp-01` (0,032266) et `btp-06` (0,032002), alors que BM25 seul aurait mis le modèle générique en premier.

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — Cette fonction est le comptable de la paie qui applique la règle de fin de service du secteur privé : elle reçoit le salaire de base mensuel et le nombre d'années de service, renvoie 0 en dessous d'un an, calcule le salaire journalier comme la base divisée par 30, compte 21 jours par année pour les cinq premières années et 30 jours au-delà, au prorata, puis plafonne le total à 24 mois de salaire de base. Pour 7 ans à 10 000 AED, elle renvoie 35 000 + 20 000 = 55 000 AED ; c'est l'outil qui fournit le montant que le cas RH doit citer, au lieu de le faire inventer par le modèle.

**`dedupliquer(retrouves)`** — C'est le portier des étapes 26 et 27, qui ne laisse entrer chaque document qu'une fois et à sa meilleure place : la fonction reçoit la liste ordonnée des identifiants, la fait passer par `dict.fromkeys`, qui ne garde que la première occurrence de chaque clé dans l'ordre d'arrivée, et renvoie la liste nettoyée. Les fonctions `recall_at_k` et `first_relevant_rank` l'appellent avant de compter, pour qu'un doublon ne prenne pas deux places dans le top-k.

**`recall_at_k(retrouves, pertinents, k)`** — C'est le pêcheur de l'étape 25, qui compte la part des poissons connus remontés dans ses k premiers casiers : la fonction reçoit la liste des morceaux retrouvés, l'ensemble des pertinents et k, lève `ValueError` si k est inférieur à 1, renvoie `None` s'il n'y a aucun pertinent, et sinon divise le nombre de pertinents présents dans les k premiers résultats dédoublonnés par le nombre total de pertinents. Elle vaut 1 pour la banque, 0,75 pour l'immobilier et 0,5 pour le BTP, et `None` pour la question hors corpus, qui s'évalue par l'abstention.

**`first_relevant_rank(retrouves, pertinents)`** — C'est le lecteur de l'étape 27 qui descend la liste, doigt sur la page, jusqu'au premier morceau utile : la fonction reçoit la liste des morceaux retrouvés et l'ensemble des pertinents, dédoublonne la liste, la parcourt en numérotant les rangs à partir de 1 et renvoie le rang du premier pertinent, ou `None` si elle n'en trouve aucun. Le programme s'en sert pour comparer BM25 seul et la fusion sur le cas BTP : avec BM25 seul, le premier pertinent n'arrive qu'au rang 2.

**`reciprocal_rank(rang, k)`** — C'est le barème de l'étape 27, qui transforme un rang en note : la fonction reçoit un rang, ou `None`, et une coupure k facultative, renvoie 0 si le rang vaut `None`, lève `ValueError` pour un rang qui n'est pas un entier au moins égal à 1, renvoie encore 0 si le rang dépasse la coupure, et sinon 1 / rang. Sur le cas BTP, elle donne 0,5 avec BM25 seul et 1 après la fusion, et la moyenne de ses valeurs sur les sept questions évaluables, le MRR, vaut exactement 1.

**`dcg_at_k(rels, k)`** — C'est le caissier de l'étape 28, qui additionne la valeur des morceaux servis en accordant une remise d'autant plus forte qu'ils arrivent tard : la fonction reçoit la liste des notes dans l'ordre du classement et la profondeur k, lève `ValueError` si k est inférieur à 1, puis additionne, pour chacun des k premiers rangs, le gain 2 élevé à la note, moins 1, divisé par log₂(rang + 1). Elle renvoie ce total, qui sert à la fois au DCG du classement réel et à l'IDCG du classement idéal dans `ndcg_at_k`.

**`ndcg_at_k(rels_retrouves, rels_tous_juges, k)`** — C'est la comparaison de l'étape 28 entre le repas servi et le meilleur repas possible : la fonction reçoit les notes des morceaux retrouvés, celles de tous les morceaux jugés et k, lève `ValueError` si la liste retrouvée contient une note pertinente absente des jugements, calcule l'IDCG sur toutes les notes jugées triées par ordre décroissant, et renvoie `None` si cet IDCG est nul, sinon le rapport du DCG retrouvé à l'IDCG. Elle donne 1 pour la banque, 0,9341 pour l'immobilier et 0,7277 pour la crypto, et la somme de ses sept valeurs vaut 6,4513.

**`fmt(v)`** — Cette petite fonction est le typographe du tableau final : elle reçoit un nombre ou `None`, et renvoie soit un tiret cadratin entouré d'espaces quand la valeur n'existe pas, soit le nombre écrit avec deux décimales. Elle permet d'aligner proprement les colonnes R@k, RR, NDCG et fidélité, y compris pour la question hors corpus, dont toutes les métriques valent `None` et s'affichent comme des tirets plutôt que comme des zéros trompeurs.

**`rechercher(cas, normaliser_texte)`** — C'est le documentaliste qui, pour une question, interroge deux bibliothécaires aux méthodes opposées puis réconcilie leurs listes : la fonction reçoit un `Cas` et un drapeau de normalisation, vrai par défaut, découpe la question et chaque morceau avec `tokeniser`, calcule le score BM25 et le cosinus de chaque morceau, garde dans le classement lexical les seuls morceaux de score positif, trie tous les morceaux par cosinus, fusionne les deux listes par `rrf` et retient les k premiers. Elle renvoie un dictionnaire avec les deux classements, le top-k et les deux tables de scores ; sans normalisation, le morceau arabe `pub-01` obtient un BM25 nul, avec normalisation 3,6851.

**`construire_prompt(question, sources)`** — Voici le greffier qui prépare le dossier remis au modèle : la fonction reçoit la question et la liste des sources retenues, chacune sous la forme d'un dictionnaire avec un identifiant et un texte, écrit une première ligne de consigne qui exige de répondre uniquement à partir des sources et de citer chaque fait avec son identifiant, ajoute une ligne `[id] texte` par source, puis la question. Elle renvoie ce texte, lignes jointes par des retours à la ligne ; pour la banque, il contient trois lignes de sources et se termine par « client retraité ? », ce que `main` vérifie.

**`fidelite_approchee(reponse, sources)`** — Cette fonction est le vérificateur de faits qui relit la réponse phrase par phrase, crayon rouge à la main : elle reçoit la réponse du modèle et le dictionnaire des sources fournies, découpe la réponse en phrases, renvoie `None` et une liste vide si elle n'en trouve aucune, puis rejette chaque phrase qui ne cite aucune source ou cite une source jamais fournie, qui contient un nombre absent des sources citées, ou dont moins de la moitié des mots pleins figurent dans ces sources. Elle renvoie la part des phrases étayées et la liste des phrases rejetées : 0,5 pour l'assurance, dont la franchise de 250 AED contredit les 500 AED du contrat ; et le programme montre qu'elle peut aussi accepter un faux et refuser un vrai.

**`decider(cos_max, fidelite, perimes_cites)`** — C'est le garde-fou posté à la sortie, un aiguilleur qui envoie chaque réponse sur l'une de trois voies : la fonction reçoit le meilleur cosinus du top-k, la fidélité approchée et la liste des sources périmées citées, renvoie « abstention » si le cosinus reste sous 0,5, « revue humaine » pour fait non étayé si la fidélité est absente ou inférieure à 1, « revue humaine » pour source remplacée si une source périmée est citée, et sinon « répondre ». Elle renvoie toujours un couple (décision, motif), le motif étant vide quand l'agent peut répondre ; la crypto et l'assurance partent ainsi en revue humaine, et la question hors corpus en abstention.

**`executer_cas(cas)`** — C'est le metteur en scène d'un cas complet, du premier appel d'outil jusqu'au bulletin de notes : la fonction reçoit un `Cas`, prépare les deux outils internes, lance `executer_agent` avec un `FakeLLM` qui joue le script du cas, reconstruit à partir de la trace les sources que le modèle a réellement reçues, résultats d'outils compris, calcule le meilleur cosinus, la fidélité approchée (sauf si l'agent doit s'abstenir), les sources périmées citées et la décision, puis, si la question a au moins un pertinent, le Recall@k, le rang réciproque et le NDCG@k. Elle renvoie un dictionnaire qui rassemble tout cela, ainsi que le prompt tel que le modèle l'aurait lu.

**`outil_rechercher(question)`** — Cette fonction interne, définie dans `executer_cas`, est le guichet de recherche que le modèle peut appeler : elle reçoit une question, lance `rechercher` sur le cas en cours, garde au passage tous les classements et les scores dans le mémo `memo` pour l'évaluation ultérieure, et renvoie au modèle la seule liste des morceaux du top-k, chacun réduit à son identifiant et à son texte. L'argument `question` qu'elle reçoit n'est pas utilisé : c'est la question du cas, déjà connue de `rechercher`, qui sert à la recherche.

**`outil_fin_de_service(salaire_base_aed, annees)`** — Cette autre fonction interne de `executer_cas` est le guichet de calcul que le modèle appelle au lieu de faire lui-même l'arithmétique : elle reçoit le salaire de base en dirhams et le nombre d'années, appelle `gratuite_fin_de_service`, arrondit le résultat à deux décimales, et renvoie un dictionnaire qui reprend les deux arguments, l'indemnité et une phrase d'explication de la règle. Dans le cas RH, elle rend 55 000 AED pour 7 ans à 10 000 AED, et ce résultat devient une source citable sous l'identifiant `outil:fin_de_service`.

**`script(question, reponse, autres_outils)`** — C'est le scénariste qui écrit à l'avance toutes les répliques du faux LLM pour un cas : la fonction reçoit la question, le texte de la réponse finale et, en nombre variable, des couples (nom d'outil, arguments). Elle fabrique d'abord une réponse qui appelle l'outil `rechercher` avec l'identifiant `t1`, puis une réponse par outil supplémentaire avec les identifiants `t2`, `t3` et ainsi de suite, et enfin une réponse « end_turn » qui contient le texte final ; elle renvoie cette liste de `Reponse`, que `FakeLLM` jouera dans l'ordre.

**`les_cas()`** — Cette fonction est le recueil des huit scènes jouées par le programme : elle ne reçoit rien et renvoie une liste de `Cas`, la banque, l'immobilier, la crypto, l'assurance, les ressources humaines, le BTP, le secteur public en arabe et en anglais, et une question hors corpus sur un permis de pêche. Chaque cas porte sa question, le vecteur jouet de cette question, ses morceaux avec leurs notes de pertinence et leurs drapeaux de péremption, la profondeur k, 3 partout sauf 4 pour les ressources humaines, et le script du faux LLM, y compris les erreurs volontaires de l'assurance et de la crypto.

**`main()`** — Le chef d'orchestre exécute les huit cas, affiche et vérifie le prompt de la banque, puis imprime le tableau du top-k, du Recall@k, du rang réciproque, du NDCG, de la fidélité, du meilleur cosinus et de la décision, qu'il confronte au dictionnaire `attendu`. Il vérifie ensuite un à un les modes d'échec, la phrase rejetée de l'assurance, la source remplacée de la crypto, les deux outils et les 55 000 AED du cas RH, le rang réciproque de 0,5 avec BM25 seul pour le BTP, le BM25 nul sans normalisation de l'arabe et l'abstention hors corpus, puis les nombres de la démonstration. Il termine par les moyennes sur les sept questions évaluables, R@k 0,8214, MRR 1 et NDCG 0,9216, et la ligne finale n'annonce le succès que si chaque `assert` a tenu.

```python
"""Étape 29 — Sept RAG jouets de bout en bout : BM25 + cosinus, fusion RRF, prompt cité, fidélité approchée, métriques."""
import json
import math
import re
import sys
import unicodedata
from collections import Counter
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


# ---------------------------------------------------------------- recherche et fin de service (code canonique)
def cosinus(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("dimensions différentes")
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        raise ValueError("vecteur nul : le cosinus n'est pas défini")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))


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


def rrf(classements: list[list[str]], k_rrf: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion ; un document absent d'un classement y contribue 0. Sortie triée, égalités par nom."""
    scores: dict[str, float] = {}
    for classement in classements:
        for rang, doc in enumerate(classement, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k_rrf + rang)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float:
    """Décret-loi fédéral 33/2021 (secteur privé, hors ressortissants émiriens et hors DIFC) :
    au moins 1 an de service ; salaire journalier = base / 30 ; 21 jours par an les 5 premières années,
    30 jours au-delà, au prorata ; plafond : 24 mois de salaire de base."""
    if annees < 1:
        return 0.0
    jour = salaire_base_mensuel / 30
    brut = min(annees, 5) * 21 * jour + max(annees - 5, 0) * 30 * jour
    return min(brut, 24 * salaire_base_mensuel)


# ---------------------------------------------------------------- métriques (étapes 25 à 28)
def dedupliquer(retrouves: list[str]) -> list[str]:
    return list(dict.fromkeys(retrouves))


def recall_at_k(retrouves: list[str], pertinents: set[str], k: int) -> float | None:
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    if not pertinents:
        return None
    return sum(1 for d in dedupliquer(retrouves)[:k] if d in pertinents) / len(pertinents)


def first_relevant_rank(retrouves: list[str], pertinents: set[str]) -> int | None:
    for rang, doc in enumerate(dedupliquer(retrouves), start=1):
        if doc in pertinents:
            return rang
    return None


def reciprocal_rank(rang: int | None, k: int | None = None) -> float:
    if rang is None:
        return 0.0
    if isinstance(rang, bool) or not isinstance(rang, int) or rang < 1:
        raise ValueError(f"rang invalide : {rang!r}")
    if k is not None and rang > k:
        return 0.0
    return 1.0 / rang


def dcg_at_k(rels: list[int], k: int) -> float:
    if k < 1:
        raise ValueError("k doit être un entier >= 1")
    return sum((2 ** rel - 1) / math.log2(i + 1) for i, rel in enumerate(rels[:k], start=1))


def ndcg_at_k(rels_retrouves: list[int], rels_tous_juges: list[int], k: int) -> float | None:
    if Counter(r for r in rels_retrouves if r > 0) - Counter(r for r in rels_tous_juges if r > 0):
        raise ValueError("une note retrouvée est absente des jugements")
    idcg = dcg_at_k(sorted(rels_tous_juges, reverse=True), k)
    return None if idcg == 0.0 else dcg_at_k(rels_retrouves, k) / idcg


# ---------------------------------------------------------------- chaîne RAG jouet
MOTS_VIDES = {"a", "au", "aux", "ce", "d", "de", "des", "du", "elle", "en", "est", "et", "il", "l", "la", "le",
              "les", "ne", "ou", "par", "pas", "pour", "qu", "que", "quel", "quelle", "qui", "s", "sa", "se",
              "son", "sur", "un", "une", "y", "and", "do", "how", "i", "is", "of", "the", "to", "with"}
SEUIL_COSINUS = 0.5          # en dessous, rien n'est assez proche : l'agent s'abstient
SEUIL_FIDELITE = 1.0         # toutes les phrases de la réponse doivent être étayées
RECOUVREMENT_MIN = 0.5       # part minimale des mots pleins d'une phrase présents dans ses sources
ARABE = {"\N{ARABIC LETTER ALEF WITH HAMZA ABOVE}": "\N{ARABIC LETTER ALEF}",
         "\N{ARABIC LETTER ALEF WITH HAMZA BELOW}": "\N{ARABIC LETTER ALEF}",
         "\N{ARABIC LETTER ALEF WITH MADDA ABOVE}": "\N{ARABIC LETTER ALEF}",
         "\N{ARABIC LETTER TEH MARBUTA}": "\N{ARABIC LETTER HEH}"}


def normaliser(t: str) -> str:
    """Minuscules ; formes de l'alef et ta marbuta unifiées ; accents latins et diacritiques arabes retirés."""
    t = "".join(ARABE.get(c, c) for c in t.lower())
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def tokeniser(t: str, normaliser_texte: bool = True) -> list[str]:
    brut = normaliser(t) if normaliser_texte else t.lower()      # sans normalisation : minuscules seulement
    return [m for m in re.findall(r"[^\W_]+", brut) if m not in MOTS_VIDES]


def fmt(v: float | None) -> str:
    return " —  " if v is None else f"{v:.2f}"


def nombres(t: str) -> set[float]:
    """Nombres d'un texte ; « 1 450 » et « 1450 » donnent la même valeur ; « 2,5 » donne 2.5."""
    blanc = r"[ \N{NO-BREAK SPACE}\N{NARROW NO-BREAK SPACE}]"        # espace, insécable ou fine insécable
    trouves = re.findall(r"\d{1,3}(?:" + blanc + r"\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?", t)
    return {float(re.sub(blanc, "", n).replace(",", ".")) for n in trouves}


@dataclass
class Morceau:
    id: str
    texte: str
    vecteur: list[float]      # plongement jouet écrit à la main (axes décrits dans chaque cas)
    note: int = 0             # jugement de pertinence de 0 à 3 : la vérité terrain de l'évaluation
    perime: bool = False      # version remplacée d'un document


@dataclass
class Cas:
    domaine: str
    question: str
    vecteur_question: list[float]
    morceaux: list[Morceau]
    k: int
    script: list              # réponses prévues du faux LLM, dans l'ordre


def rechercher(cas: Cas, normaliser_texte: bool = True) -> dict:
    """BM25 et cosinus classent les morceaux, RRF fusionne les deux classements, on garde les k premiers."""
    corpus = [tokeniser(m.texte, normaliser_texte) for m in cas.morceaux]
    requete = tokeniser(cas.question, normaliser_texte)
    bm25 = {m.id: bm25_score(requete, doc, corpus) for m, doc in zip(cas.morceaux, corpus)}
    cos = {m.id: cosinus(cas.vecteur_question, m.vecteur) for m in cas.morceaux}
    par_bm25 = [d for d in sorted(bm25, key=lambda d: (-bm25[d], d)) if bm25[d] > 0]   # morceaux qui contiennent un mot de la question
    par_cos = sorted(cos, key=lambda d: (-cos[d], d))
    fusion = [d for d, _ in rrf([par_bm25, par_cos])]
    return {"bm25": par_bm25, "cos": par_cos, "top": fusion[:cas.k], "scores_bm25": bm25, "scores_cos": cos}


def construire_prompt(question: str, sources: list[dict]) -> str:
    lignes = ["Réponds uniquement à partir des sources ci-dessous et cite chaque fait avec [id]."]
    lignes += [f"[{s['id']}] {s['texte']}" for s in sources]
    lignes.append(f"Question : {question}")
    return "\n".join(lignes)


def fidelite_approchee(reponse: str, sources: dict[str, str]) -> tuple[float | None, list[str]]:
    """Part des phrases étayées : citation d'une source fournie, nombres présents, mots pleins recouverts à 50 %."""
    phrases = [p for p in re.split(r"(?<=[.!?])\s+", reponse.strip()) if p]
    if not phrases:
        return None, []
    non_etayees = []
    for p in phrases:
        cites = re.findall(r"\[([^\]]+)\]", p)
        corps = re.sub(r"\[[^\]]+\]", " ", p)
        if not cites or any(c not in sources for c in cites):
            non_etayees.append(p)                     # pas de citation, ou citation d'une source jamais fournie
            continue
        texte_cite = " ".join(sources[c] for c in cites)
        if not nombres(corps) <= nombres(texte_cite):
            non_etayees.append(p)                     # un nombre absent des sources citées
            continue
        mots = {m for m in tokeniser(corps) if not m.isdigit()}
        if mots and len(mots & set(tokeniser(texte_cite))) / len(mots) < RECOUVREMENT_MIN:
            non_etayees.append(p)                     # la phrase parle d'autre chose que ses sources
    return (len(phrases) - len(non_etayees)) / len(phrases), non_etayees


def decider(cos_max: float, fidelite: float | None, perimes_cites: list[str]) -> tuple[str, str]:
    """Garde-fou de sortie : trois seuils, dans cet ordre."""
    if cos_max < SEUIL_COSINUS:
        return "abstention", "rien d'assez proche"
    if fidelite is None or fidelite < SEUIL_FIDELITE:
        return "revue humaine", "fait non étayé"
    if perimes_cites:
        return "revue humaine", "source remplacée citée"
    return "répondre", ""


def executer_cas(cas: Cas) -> dict:
    """Agent RAG complet : outils, boucle canonique, garde-fou de sortie, puis métriques d'évaluation."""
    par_id = {m.id: m for m in cas.morceaux}
    memo: dict = {}

    def outil_rechercher(question: str) -> list[dict]:
        memo.update(rechercher(cas))
        return [{"id": d, "texte": par_id[d].texte} for d in memo["top"]]

    def outil_fin_de_service(salaire_base_aed: float, annees: float) -> dict:
        return {"salaire_base_aed": salaire_base_aed, "annees": annees,
                "indemnite_aed": round(gratuite_fin_de_service(salaire_base_aed, annees), 2),
                "detail": "5 ans à 21 jours puis le reste à 30 jours, salaire journalier = base / 30"}

    outils = {"rechercher": outil_rechercher, "fin_de_service": outil_fin_de_service}
    r = executer_agent(FakeLLM(cas.script), "Agent RAG : réponds avec des citations [id].", cas.question, outils, [])
    sources: dict[str, str] = {}
    for nom, _, sortie in r["trace"]:
        if nom == "rechercher":
            sources.update({s["id"]: s["texte"] for s in sortie})
        else:
            sources[f"outil:{nom}"] = json.dumps(sortie, ensure_ascii=False)   # un résultat d'outil est une source
    cos_max = max(memo["scores_cos"][d] for d in memo["top"])
    fid, non_etayees = (None, []) if cos_max < SEUIL_COSINUS else fidelite_approchee(r["reponse"], sources)
    perimes = sorted(c for c in set(re.findall(r"\[([^\]]+)\]", r["reponse"])) if c in par_id and par_id[c].perime)
    decision, motif = decider(cos_max, fid, perimes)
    jugements = {m.id: m.note for m in cas.morceaux}
    pertinents = {d for d, n in jugements.items() if n > 0}
    recall = rr = ndcg = None
    if pertinents:                                    # une question sans pertinent s'évalue par l'abstention
        recall = recall_at_k(memo["top"], pertinents, cas.k)
        rr = reciprocal_rank(first_relevant_rank(memo["top"], pertinents), cas.k)
        ndcg = ndcg_at_k([jugements[d] for d in memo["top"]], list(jugements.values()), cas.k)
    return {"top": memo["top"], "bm25": memo["bm25"], "cos": memo["cos"], "scores_bm25": memo["scores_bm25"],
            "outils": [t[0] for t in r["trace"]], "trace": r["trace"], "fidelite": fid, "non_etayees": non_etayees,
            "perimes": perimes, "cos_max": cos_max, "decision": decision, "motif": motif,
            "recall": recall, "rr": rr, "ndcg": ndcg, "pertinents": pertinents,
            "prompt": construire_prompt(cas.question, [{"id": d, "texte": par_id[d].texte} for d in memo["top"]])}


def script(question: str, reponse: str, *autres_outils: tuple[str, dict]) -> list:
    """Le faux LLM appelle « rechercher », puis les autres outils prévus, puis répond."""
    etapes = [Reponse("tool_use", [appel_outil("rechercher", {"question": question}, "t1")])]
    for i, (nom, args) in enumerate(autres_outils, start=2):
        etapes.append(Reponse("tool_use", [appel_outil(nom, args, f"t{i}")]))
    etapes.append(Reponse("end_turn", [texte(reponse)]))
    return etapes


def les_cas() -> list[Cas]:
    cas = []
    # BANQUE — axes : [endettement, retraite, cartes, finance islamique]
    q = "Quel plafond d'endettement s'applique à un client retraité ?"
    cas.append(Cas("BANQUE", q, [0.85, 0.75, 0.05, 0.0], [
        Morceau("banque-01", "Le ratio d'endettement total, toutes mensualités comprises, ne doit pas dépasser 50 % du salaire ou du revenu régulier.", [0.95, 0.1, 0.05, 0.0], 2),
        Morceau("banque-02", "Pour un client retraité, le plafond du ratio d'endettement est de 30 % du revenu régulier.", [0.8, 0.95, 0.0, 0.0], 3),
        Morceau("banque-03", "Toutes les mensualités existantes, y compris celle du nouveau prêt, entrent dans le calcul du ratio.", [0.85, 0.05, 0.2, 0.0], 2),
        Morceau("banque-04", "Les frais annuels de la carte de crédit sont prélevés le mois anniversaire de l'ouverture.", [0.05, 0.0, 0.95, 0.0]),
        Morceau("banque-05", "La Murabaha est une vente avec une marge connue à l'avance, utilisée pour financer un véhicule.", [0.1, 0.0, 0.0, 0.95]),
        Morceau("banque-06", "Un prêt personnel ne peut pas dépasser 20 fois le salaire mensuel, sur 48 mois au plus.", [0.5, 0.0, 0.2, 0.0]),
    ], 3, script(q, "Pour un client retraité, le plafond du ratio d'endettement est de 30 % du revenu régulier [banque-02]. "
                    "Toutes les mensualités existantes, y compris celle du nouveau prêt, entrent dans ce calcul [banque-03].")))
    # IMMO — axes : [quartier JVC, deux chambres, villa, bureau]
    q = "Quel prix au sqft pour un appartement deux-chambres à Jumeirah Village Circle ?"
    cas.append(Cas("IMMO", q, [0.9, 0.85, 0.0, 0.0], [
        Morceau("immo-01", "Vente JVC, appartement deux-chambres de 1 120 sqft, 1 450 AED/sqft, septembre.", [0.9, 0.9, 0.0, 0.0], 3),
        Morceau("immo-02", "Vente JVC, appartement deux-chambres de 1 050 sqft avec grand balcon et vue sur le parc, 1 480 AED/sqft, août.", [0.7, 0.75, 0.25, 0.0], 3),
        Morceau("immo-03", "Vente JVT, appartement deux-chambres de 1 100 sqft, 1 390 AED/sqft, juin.", [0.75, 0.9, 0.0, 0.0], 1),
        Morceau("immo-04", "Vente JVC, villa de quatre chambres, 2 100 AED/sqft, juillet.", [0.9, 0.2, 0.9, 0.0]),
        Morceau("immo-05", "Location JLT, bureau de 900 sqft, loyer annuel payable en quatre chèques.", [0.1, 0.0, 0.0, 0.95]),
        Morceau("immo-06", "Vente JVC, appartement une chambre de 760 sqft, 1 520 AED/sqft, juillet.", [0.9, 0.4, 0.0, 0.0], 1),
    ], 3, script(q, "Deux ventes d'appartements deux-chambres à JVC donnent 1 450 et 1 480 AED/sqft [immo-01][immo-02]. "
                    "Une vente à JVT, quartier voisin, donne 1 390 AED/sqft [immo-03].")))
    # CRYPTO — axes : [retrait, KYC, dépôt, liquidité]
    q = "Quelle est la limite de retrait quotidienne d'un compte vérifié ?"
    cas.append(Cas("CRYPTO", q, [0.9, 0.3, 0.1, 0.0], [
        Morceau("crypto-01", "Grille des frais 2026, en vigueur : la limite de retrait quotidienne d'un compte vérifié est de 50 000 AED, sauf demande motivée.", [0.8, 0.35, 0.15, 0.0], 3),
        Morceau("crypto-02", "Grille 2025, remplacée : limite de retrait quotidienne d'un compte vérifié, 20 000 AED.", [0.9, 0.3, 0.05, 0.0], 1, perime=True),
        Morceau("crypto-03", "La vérification KYC d'un compte exige une pièce d'identité valide et un justificatif d'adresse.", [0.2, 0.95, 0.0, 0.0], 1),
        Morceau("crypto-04", "Les dépôts en stablecoins sont crédités après six confirmations sur la chaîne.", [0.1, 0.0, 0.95, 0.1]),
        Morceau("crypto-05", "Une alerte de liquidité se déclenche quand un pool descend sous son seuil.", [0.05, 0.0, 0.1, 0.95]),
    ], 3, script(q, "La limite de retrait quotidienne d'un compte vérifié est de 20 000 AED [crypto-02].")))
    # ASSUR — axes : [bris de glace, franchise, santé, vol]
    q = "Le bris de pare-brise est-il couvert, et quelle franchise s'applique ?"
    cas.append(Cas("ASSUR", q, [0.85, 0.5, 0.0, 0.0], [
        Morceau("assur-01", "La garantie bris de glace couvre le pare-brise, les vitres latérales et la lunette arrière.", [0.95, 0.1, 0.0, 0.0], 3),
        Morceau("assur-02", "Une franchise de 500 AED s'applique à chaque sinistre bris de glace.", [0.7, 0.7, 0.0, 0.0], 3),
        Morceau("assur-03", "Les dommages antérieurs à la souscription sont exclus de toutes les garanties.", [0.3, 0.3, 0.1, 0.1], 2),
        Morceau("assur-04", "La garantie santé rembourse les consultations à 80 % dans le réseau agréé.", [0.0, 0.1, 0.95, 0.0]),
        Morceau("assur-05", "En cas de vol, la déclaration doit être faite sous 48 heures.", [0.05, 0.0, 0.0, 0.95]),
        Morceau("assur-06", "La vétusté est déduite de l'indemnité au-delà de trois ans d'ancienneté du véhicule.", [0.3, 0.2, 0.0, 0.2], 1),
    ], 3, script(q, "Le bris de pare-brise est couvert par la garantie bris de glace [assur-01]. "
                    "Une franchise de 250 AED s'applique à chaque sinistre bris de glace [assur-02].")))
    # RH — axes : [fin de service, régime particulier (DIFC, GPSSA), visa]
    q = "Quelle indemnité de fin de service pour 7 ans de service avec un salaire de base de 10 000 AED ?"
    cas.append(Cas("RH", q, [0.95, 0.1, 0.0], [
        Morceau("rh-01", "Secteur privé : 21 jours de salaire de base par année de service pour les cinq premières années.", [0.95, 0.05, 0.0], 3),
        Morceau("rh-02", "Au-delà de cinq ans, l'indemnité de fin de service est de 30 jours de salaire de base par année de service.", [0.95, 0.05, 0.0], 3),
        Morceau("rh-03", "L'indemnité totale ne peut pas dépasser 24 mois de salaire de base.", [0.85, 0.05, 0.0], 2),
        Morceau("rh-04", "Le salaire journalier se calcule en divisant le salaire de base mensuel par 30.", [0.8, 0.0, 0.05], 2),
        Morceau("rh-05", "Les salariés du DIFC relèvent d'un régime d'épargne distinct pour la fin de service.", [0.6, 0.8, 0.0]),
        Morceau("rh-06", "Les ressortissants émiriens relèvent de la GPSSA.", [0.3, 0.9, 0.0]),
        Morceau("rh-07", "Le visa de travail est renouvelé après accord du MOHRE.", [0.05, 0.1, 0.95]),
    ], 4, script(q, "Pour les cinq premières années, l'indemnité est de 21 jours de salaire de base par année de service [rh-01]. "
                    "Au-delà de cinq ans, elle est de 30 jours de salaire de base par année de service [rh-02]. "
                    "Pour 7 ans à 10 000 AED de salaire de base, l'outil de calcul donne une indemnité de 55 000 AED [outil:fin_de_service].",
                 ("fin_de_service", {"salaire_base_aed": 10000, "annees": 7}))))
    # BTP — axes : [retenue de garantie, lot électricité, TVA, planning]
    q = "Quelle retenue de garantie appliquer à la facture du lot électricité ?"
    cas.append(Cas("BTP", q, [0.8, 0.6, 0.1, 0.0], [
        Morceau("btp-01", "Modèle générique : retenue de garantie de 5 % sur chaque facture.", [0.9, 0.0, 0.2, 0.0]),
        Morceau("btp-02", "Contrat de sous-traitance du lot électricité : la retenue de garantie est de 10 %, libérée à la réception des travaux.", [0.75, 0.65, 0.05, 0.0], 3),
        Morceau("btp-03", "La TVA standard de 5 % s'applique aux factures de travaux.", [0.2, 0.0, 0.95, 0.0], 1),
        Morceau("btp-04", "Le lot plomberie prévoit une retenue de 7 % et une pénalité de retard journalière.", [0.7, 0.0, 0.0, 0.2]),
        Morceau("btp-05", "Les situations de travaux sont validées par le maître d'œuvre avant paiement.", [0.3, 0.1, 0.2, 0.3]),
        Morceau("btp-06", "Planning du lot électricité : raccordement au réseau prévu en mars.", [0.4, 0.9, 0.0, 0.2]),
    ], 3, script(q, "La facture du lot électricité supporte une retenue de garantie de 10 %, libérée à la réception des travaux [btp-02].")))
    # PUBLIC — axes : [renouvellement de l'Emirates ID, carte perdue, visa, horaires, autres démarches]
    q = "بطاقه الهويه الاماراتيه renewal"      # « carte d'identité émiratie », ta marbuta écrite ha, alef sans hamza
    pages = [
        Morceau("pub-01", "تجديد بطاقة الهوية الإماراتية عبر الإنترنت باستخدام UAE Pass", [0.95, 0.1, 0.0, 0.0, 0.0], 3),
        Morceau("pub-02", "Emirates ID renewal: apply online with UAE Pass and upload a recent photo.", [0.9, 0.1, 0.05, 0.0, 0.0], 3),
        Morceau("pub-03", "Replacing a lost card follows a separate procedure.", [0.4, 0.9, 0.0, 0.0, 0.0], 1),
        Morceau("pub-04", "Visa status can be checked online.", [0.1, 0.0, 0.95, 0.0, 0.0]),
        Morceau("pub-05", "مواعيد عمل مراكز الخدمة", [0.1, 0.0, 0.0, 0.95, 0.0]),
    ]
    cas.append(Cas("PUBLIC", q, [0.9, 0.15, 0.0, 0.05, 0.0], pages, 3,
                   script(q, "Emirates ID renewal is done online with UAE Pass [pub-01][pub-02].")))
    q = "How do I get a fishing permit?"
    cas.append(Cas("PUBLIC-2", q, [0.05, 0.0, 0.05, 0.05, 0.99], [Morceau(m.id, m.texte, m.vecteur) for m in pages], 3,
                   script(q, "Je ne trouve pas cette démarche dans les pages du service ; je vous oriente vers un agent.")))
    return cas


def main() -> None:
    tous_cas = les_cas()
    res = {c.domaine: executer_cas(c) for c in tous_cas}

    print("Prompt du cas BANQUE, tel que le modèle le lit :")
    for ligne in res["BANQUE"]["prompt"].split("\n"):
        print(f"  {ligne}")
    assert res["BANQUE"]["prompt"].count("\n[banque-") == 3 and res["BANQUE"]["prompt"].endswith("client retraité ?")

    print("Domaine   top-k après fusion RRF            R@k   RR    NDCG  fidélité  cos max  décision")
    for c in tous_cas:
        r = res[c.domaine]
        decision = r["decision"] + (f" ({r['motif']})" if r["motif"] else "")
        print(f"{c.domaine:<9} {', '.join(r['top']):<33} {fmt(r['recall'])}  {fmt(r['rr'])}  {fmt(r['ndcg'])}  {fmt(r['fidelite'])}      "
              f"{r['cos_max']:.2f}     {decision}")

    attendu = {   # top-k, R@k, RR, NDCG@k, fidélité, décision
        "BANQUE": (["banque-02", "banque-01", "banque-03"], 1.0, 1.0, 1.0, 1.0, "répondre"),
        "IMMO": (["immo-01", "immo-03", "immo-02"], 0.75, 1.0, 0.9341, 1.0, "répondre"),
        "CRYPTO": (["crypto-02", "crypto-01", "crypto-03"], 1.0, 1.0, 0.7277, 1.0, "revue humaine"),
        "ASSUR": (["assur-02", "assur-01", "assur-03"], 0.75, 1.0, 1.0, 0.5, "revue humaine"),
        "RH": (["rh-02", "rh-03", "rh-01", "rh-05"], 0.75, 1.0, 0.8722, 1.0, "répondre"),
        "BTP": (["btp-02", "btp-01", "btp-06"], 0.5, 1.0, 0.9173, 1.0, "répondre"),
        "PUBLIC": (["pub-01", "pub-02", "pub-03"], 1.0, 1.0, 1.0, 1.0, "répondre"),
    }
    for dom, (top, rec, rr, ndcg, fid, dec) in attendu.items():
        r = res[dom]
        assert r["top"] == top and r["decision"] == dec, dom
        assert (r["recall"], r["rr"], round(r["ndcg"], 4), r["fidelite"]) == (rec, rr, ndcg, fid), dom

    # Les modes d'échec, un par un.
    assur = res["ASSUR"]["non_etayees"]
    assert assur == ["Une franchise de 250 AED s'applique à chaque sinistre bris de glace [assur-02]."]
    assert res["CRYPTO"]["perimes"] == ["crypto-02"] and res["CRYPTO"]["fidelite"] == 1.0
    assert res["RH"]["outils"] == ["rechercher", "fin_de_service"] and res["RH"]["trace"][1][2]["indemnite_aed"] == 55000.0
    assert "rh-05" in res["RH"]["top"] and "rh-04" not in res["RH"]["top"]           # le régime du DIFC entre, le salaire journalier sort
    btp_bm25_seul = reciprocal_rank(first_relevant_rank(res["BTP"]["bm25"], res["BTP"]["pertinents"]), 3)
    assert res["BTP"]["bm25"][0] == "btp-01" and btp_bm25_seul == 0.5             # BM25 seul : le modèle générique en tête
    cas_pub = next(c for c in tous_cas if c.domaine == "PUBLIC")
    sans_norm = rechercher(cas_pub, normaliser_texte=False)["scores_bm25"]["pub-01"]
    avec_norm = res["PUBLIC"]["scores_bm25"]["pub-01"]
    assert sans_norm == 0.0 and avec_norm > 0 and res["PUBLIC"]["bm25"] == ["pub-01", "pub-02"]
    assert res["PUBLIC-2"]["decision"] == "abstention" and res["PUBLIC-2"]["recall"] is None and res["PUBLIC-2"]["cos_max"] < 0.5

    # Démonstration, point 1 : l'arithmétique de la fusion RRF sur le cas BTP.
    fusion_btp = [(d, round(s, 6)) for d, s in rrf([res["BTP"]["bm25"], res["BTP"]["cos"]])[:3]]
    assert res["BTP"]["bm25"][:3] == ["btp-01", "btp-02", "btp-06"] and res["BTP"]["cos"][:3] == ["btp-02", "btp-06", "btp-01"]
    assert fusion_btp == [("btp-02", 0.032522), ("btp-01", 0.032266), ("btp-06", 0.032002)]
    assert [round(res["BTP"]["scores_bm25"][d], 4) for d in ("btp-01", "btp-02", "btp-06", "btp-04")] == [3.4273, 2.9152, 1.8094, 1.3731]
    assert [round(cosinus(c.vecteur_question, m.vecteur), 4) for c in tous_cas if c.domaine == "BTP"
            for m in c.morceaux if m.id in ("btp-02", "btp-06", "btp-01")] == [0.7987, 0.9963, 0.8515]
    # Démonstration, point 3 : la fidélité approchée n'est ni suffisante ni nécessaire.
    src_banque = {s["id"]: s["texte"] for s in res["BANQUE"]["trace"][0][2]}
    faux_accepte = "Pour un client retraité, le plafond du ratio d'endettement est de 50 % du revenu régulier [banque-01][banque-02]."
    vrai_refuse = "Un retraité ne peut consacrer plus de 30 % de ses ressources au remboursement de ses crédits [banque-02]."
    assert fidelite_approchee(faux_accepte, src_banque)[0] == 1.0      # faux, et pourtant accepté
    assert fidelite_approchee(vrai_refuse, src_banque)[0] == 0.0       # fidèle, et pourtant refusé
    mots_pleins = {m for m in tokeniser(vrai_refuse.split("[")[0]) if not m.isdigit()}
    assert len(mots_pleins) == 8 and mots_pleins & set(tokeniser(src_banque["banque-02"])) == {"retraite"}
    # Démonstration, point 4 : le montant de fin de service vient de l'outil, pas d'un document.
    assert 5 * 21 * 10000 / 30 == 35000 and 2 * 30 * 10000 / 30 == 20000 and gratuite_fin_de_service(10000, 7) == 55000
    assert nombres("1 450 AED, soit 2,5 %") == {1450.0, 2.5} == nombres("1\N{NO-BREAK SPACE}450 AED et 2.5")
    assert normaliser("بطاقة الهوية الإماراتية") == normaliser("بطاقه الهويه الاماراتيه")

    print(f"Échecs repérés : ASSUR « {assur[0][:45]}… » ; CRYPTO cite {res['CRYPTO']['perimes'][0]}, version remplacée")
    print(f"Fusion utile : BTP, RR avec BM25 seul = {btp_bm25_seul:.2f}, après fusion = {res['BTP']['rr']:.2f} ; "
          f"PUBLIC, BM25(pub-01) sans normalisation = {sans_norm:.2f}, avec = {avec_norm:.2f}")
    print(f"Outils RH : {' → '.join(res['RH']['outils'])}, indemnité {res['RH']['trace'][1][2]['indemnite_aed']} AED citée [outil:fin_de_service]")

    evaluables = [r for r in res.values() if r["recall"] is not None]
    moy = {m: sum(r[m] for r in evaluables) / len(evaluables) for m in ("recall", "rr", "ndcg")}
    abst = sum(1 for d, r in res.items() if r["recall"] is None and r["decision"] == "abstention")
    print(f"Moyennes sur {len(evaluables)} questions évaluables : R@k {moy['recall']:.4f} · MRR {moy['rr']:.4f} · "
          f"NDCG {moy['ndcg']:.4f} ; abstention correcte {abst}/1")
    assert len(evaluables) == 7 and abst == 1
    assert (round(moy["recall"], 4), moy["rr"], round(moy["ndcg"], 4)) == (0.8214, 1.0, 0.9216)
    assert sum(r["recall"] for r in evaluables) == 5.75 and round(5.75 / 8, 4) == 0.7188     # si l'on comptait 0 pour PUBLIC-2
    assert round(sum(r["ndcg"] for r in evaluables), 4) == 6.4513 and round(avec_norm, 4) == 3.6851
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Prompt du cas BANQUE, tel que le modèle le lit :
  Réponds uniquement à partir des sources ci-dessous et cite chaque fait avec [id].
  [banque-02] Pour un client retraité, le plafond du ratio d'endettement est de 30 % du revenu régulier.
  [banque-01] Le ratio d'endettement total, toutes mensualités comprises, ne doit pas dépasser 50 % du salaire ou du revenu régulier.
  [banque-03] Toutes les mensualités existantes, y compris celle du nouveau prêt, entrent dans le calcul du ratio.
  Question : Quel plafond d'endettement s'applique à un client retraité ?
Domaine   top-k après fusion RRF            R@k   RR    NDCG  fidélité  cos max  décision
BANQUE    banque-02, banque-01, banque-03   1.00  1.00  1.00  1.00      0.99     répondre
IMMO      immo-01, immo-03, immo-02         0.75  1.00  0.93  1.00      1.00     répondre
CRYPTO    crypto-02, crypto-01, crypto-03   1.00  1.00  0.73  1.00      1.00     revue humaine (source remplacée citée)
ASSUR     assur-02, assur-01, assur-03      0.75  1.00  1.00  0.50      0.97     revue humaine (fait non étayé)
RH        rh-02, rh-03, rh-01, rh-05        0.75  1.00  0.87  1.00      1.00     répondre
BTP       btp-02, btp-01, btp-06            0.50  1.00  0.92  1.00      1.00     répondre
PUBLIC    pub-01, pub-02, pub-03            1.00  1.00  1.00  1.00      1.00     répondre
PUBLIC-2  pub-04, pub-05, pub-02             —     —     —     —        0.06     abstention (rien d'assez proche)
Échecs repérés : ASSUR « Une franchise de 250 AED s'applique à chaque … » ; CRYPTO cite crypto-02, version remplacée
Fusion utile : BTP, RR avec BM25 seul = 0.50, après fusion = 1.00 ; PUBLIC, BM25(pub-01) sans normalisation = 0.00, avec = 3.69
Outils RH : rechercher → fin_de_service, indemnité 55000.0 AED citée [outil:fin_de_service]
Moyennes sur 7 questions évaluables : R@k 0.8214 · MRR 1.0000 · NDCG 0.9216 ; abstention correcte 1/1
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un bon classement ne garantit pas une bonne réponse (cas assurance), une réponse fidèle ne garantit pas une source valide (cas crypto), et un nombre calculé doit venir d'un outil (cas RH). Les métriques de classement, la fidélité et les règles de décision mesurent trois choses différentes, et un agent RAG sérieux a besoin des trois.

## Squelette algorithmique

Les cas de ce fichier sont des agents RAG complets : la recherche hybride devient un outil appelé par la boucle d'agent, un garde-fou décide de répondre, de s'abstenir ou de passer à un humain, et les métriques d'évaluation sont calculées sur chaque cas.

```text
ALGORITHME AgentRAG
ENTRÉES : question, morceaux (texte, vecteur, note de pertinence, périmé ?), k, seuils cos et fidélité
SORTIE  : (décision, réponse, Recall@k, RR@k, NDCG@k)

  OUTIL Rechercher(question)
      bm25 ← classement BM25 des morceaux qui contiennent au moins un mot de la question
      cos  ← classement par cosinus de tous les morceaux
      top  ← les k premiers de RRF([bm25, cos])
      RETOURNER les morceaux de top avec leur identifiant
  réponse, trace ← ExécuterAgent(modèle, outils = {Rechercher, outils de calcul}, question)
  sources ← textes renvoyés par Rechercher + résultats des autres outils
  cos_max ← plus grand cosinus parmi top
  SI cos_max < seuil cos ALORS décision ← « abstention »
  SINON
      fidélité ← part des nombres de la réponse présents dans les sources
      SI fidélité < seuil ALORS décision ← « revue humaine » (fait non étayé)
      SINON SI la réponse cite un morceau périmé ALORS décision ← « revue humaine »
      SINON décision ← « répondre »
  SI la question a des pertinents ALORS calculer Recall@k, RR@k, NDCG@k sur top
  RETOURNER décision, réponse, métriques
```

**Complexité.** La recherche coûte O(n × L) pour BM25 sur n morceaux de longueur L (avec le calcul simple du fichier 22), O(n × d) pour les cosinus et O(n log n) pour les tris et la fusion. La boucle d'agent ajoute ses appels au modèle, qui dominent le temps réel. Le garde-fou et les métriques coûtent O(k + longueur de la réponse).

**Du squelette au code.** `Rechercher` correspond à l'outil `outil_rechercher`, qui appelle `rechercher` (avec `bm25_score`, `cosinus` et `rrf`) ; la boucle est `executer_agent` ; la fidélité approchée est `fidelite_approchee` et la décision `decider`, avec ses trois seuils dans l'ordre. `executer_cas` enchaîne le tout et calcule les métriques avec `recall_at_k`, `reciprocal_rank`, `first_relevant_rank` et `ndcg_at_k`.

## Cas d'usage réels aux Émirats

Chaque paragraphe raconte une question du programme : la question, les morceaux, les scores, la décision et le mode d'échec qu'elle illustre. Les textes des morceaux, les seuils et les vecteurs sont illustratifs ; seules les règles réglementaires citées reprennent les chiffres vérifiés du parcours.

### Banque — un plafond qui dépend du statut du client

Un conseiller d'une banque de détail de Dubaï demande à l'assistant crédit : « Quel plafond d'endettement s'applique à un client retraité ? ». La base contient six morceaux de la politique de crédit : la règle générale des 50 % (note 2), la règle des 30 % pour un retraité (note 3), la règle qui fait entrer toutes les mensualités dans le calcul (note 2), et trois morceaux hors sujet sur les frais de carte, la Murabaha et la limite du prêt personnel. BM25 ne trouve que deux morceaux qui contiennent des mots de la question (`banque-02` avec un score de 6,21, `banque-01` avec 0,94), et c'est le cosinus qui fait entrer `banque-03` au troisième rang ; la fusion donne `banque-02`, `banque-01`, `banque-03`, soit un Recall@3, un rang réciproque et un NDCG@3 tous égaux à 1. La réponse scriptée cite `[banque-02]` pour les 30 % et `[banque-03]` pour la règle des mensualités, ses deux phrases sont étayées, et l'agent répond. Sans le cosinus, la règle des mensualités serait restée hors du contexte et la réponse aurait omis que le nouveau prêt compte lui aussi. Le contre-exemple de la démonstration montre l'échec le plus grave possible : une réponse qui attribue 50 % à un retraité passe la fidélité approchée, ce qui impose la vraie Faithfulness de l'étape 54 avant toute mise en production. Les plafonds de 50 % et de 30 % sont ceux de la CBUAE pour le crédit aux particuliers, et l'on suit la part des réponses sur les retraités qui citent bien la règle des 30 %.

### Immobilier — un comparable voisin qui passe devant

Un agent d'une agence de Dubaï reçoit : « Quel prix au sqft pour un appartement deux-chambres à Jumeirah Village Circle ? ». Six transactions sont notées de 0 à 3 : deux ventes de deux-chambres à JVC (note 3), une vente à JVT, quartier voisin (note 1), une vente d'une chambre à JVC (note 1), une villa et un bureau (note 0). BM25 ne sait pas que « JVC » abrège « Jumeirah Village Circle » : il classe sur « appartement », « deux », « chambres » et « sqft », donne le même score (1,65) aux ventes `immo-01` et `immo-03`, et place derrière elles la vente `immo-02`, dont la description longue (balcon, vue) dilue les mots utiles. Le plongement jouet rapproche lui aussi le deux-chambres de JVT de la question, si bien que la fusion donne `immo-01`, `immo-03`, `immo-02` : un rang réciproque de 1, un Recall@3 de 0,75 (la vente d'une chambre manque) et un NDCG@3 de 0,934, qui signale l'ordre imparfait. La réponse distingue les deux ventes de JVC, à 1 450 et 1 480 AED/sqft, de la vente de JVT à 1 390 AED/sqft, et elle est étayée ; l'agent répond. Le mode d'échec serait une moyenne des trois prix calculée par le modèle lui-même : elle mélangerait deux quartiers et ne figurerait dans aucune source, donc la condition (b) la rejetterait, et un tel calcul doit passer par un outil, comme dans le cas RH. La correction durable est d'enrichir l'index avec le synonyme « JVC = Jumeirah Village Circle » ; l'estimation reste indicative, et l'acheteur doit aussi prévoir les 4 % de frais de transfert du DLD. On suit le NDCG@3 par quartier.

### Crypto — fidèle à une source périmée

Un analyste d'une plateforme d'actifs virtuels agréée par la VARA demande : « Quelle est la limite de retrait quotidienne d'un compte vérifié ? ». La base contient la grille de frais en vigueur (note 3), l'ancienne grille, marquée remplacée (note 1, encore utile pour l'historique d'un dossier), une page KYC (note 1) et deux pages hors sujet. L'ancienne grille est plus courte et son vecteur jouet est un peu plus proche de la question : elle arrive en tête dans BM25 (3,90 contre 3,33) comme au cosinus, et la fusion donne `crypto-02`, `crypto-01`, `crypto-03`. Le rang réciproque vaut 1, puisqu'un document pertinent est premier, mais le NDCG@3 tombe à 0,728, parce que la note 1 passe devant la note 3 : c'est la pertinence graduée qui voit l'inversion. La réponse scriptée annonce 20 000 AED en citant `[crypto-02]` ; sa fidélité approchée vaut 1, car le nombre figure bien dans la source citée, et c'est la règle de fraîcheur qui envoie la réponse en revue humaine. La leçon est qu'une réponse fidèle n'est pas une réponse juste : elle peut être fidèle à une source qui ne s'applique plus. Une plateforme agréée doit communiquer ses conditions en vigueur ; l'équipe retire les versions remplacées de l'index de réponse (ou les fait reculer au classement) et suit la part des réponses qui citent une version remplacée, avec un objectif de zéro.

### Assurance — une franchise inventée

Un gestionnaire d'un assureur auto et santé pose la question d'un assuré : « Le bris de pare-brise est-il couvert, et quelle franchise s'applique ? ». Six clauses sont notées : la garantie bris de glace et la franchise de bris de glace (note 3), l'exclusion des dommages antérieurs (note 2), la vétusté (note 1), et deux clauses hors sujet (santé, vol). Le classement est bon : la fusion donne `assur-02`, `assur-01`, `assur-03`, avec un rang réciproque et un NDCG@3 de 1 et un Recall@3 de 0,75 (la clause de vétusté, marginale, manque). La réponse scriptée affirme pourtant une franchise de 250 AED en citant `[assur-02]`, qui dit 500 AED : la condition (b) rejette cette phrase, la fidélité approchée vaut 0,5 et la réponse part en revue humaine. La leçon est qu'un classement parfait ne garantit pas une génération fidèle, et que les deux couches se mesurent séparément : les métriques de recherche d'un côté, la fidélité de la réponse de l'autre. Une franchise fausse entraîne un paiement faux, et l'assurance est supervisée par la CBUAE. On suit la part des réponses envoyées en revue pour fait non étayé, et la part de ces revues où le gestionnaire confirme une vraie erreur, qui mesure la précision du garde-fou.

### RH — un calcul d'outil cité comme une source

Un salarié d'une entreprise cliente d'un cabinet RH multi-émirats demande : « Quelle indemnité de fin de service pour 7 ans de service avec un salaire de base de 10 000 AED ? ». La base contient sept morceaux : les règles des 21 et 30 jours (note 3), le plafond de 24 mois et le calcul du salaire journalier (note 2), et trois morceaux hors sujet pour ce salarié (régime du DIFC, GPSSA, visa). Avec k = 4, la fusion donne `rh-02`, `rh-03`, `rh-01`, `rh-05` : le morceau du DIFC entre dans le contexte parce qu'il contient « fin de service » (BM25 de 2,84), et la règle du salaire journalier en sort, d'où un Recall@4 de 0,75 et un NDCG@4 de 0,872. L'agent appelle ensuite l'outil `fin_de_service` avec 10 000 AED et 7 ans, reçoit 55 000 AED, et répond en citant `[rh-01]`, `[rh-02]` et `[outil:fin_de_service]` : ses trois phrases sont étayées, et il répond. Si le modèle avait calculé le montant lui-même, 55 000 ne figurerait dans aucune source et la phrase serait rejetée ; si le modèle s'était appuyé sur le morceau du DIFC, il aurait appliqué le mauvais régime, risque déjà relevé à l'étape 26. Le calcul suit le décret-loi fédéral 33/2021 pour le secteur privé hors zones franches, et toute réponse reste à confirmer avec le texte en vigueur avant un versement. On suit la part des montants qui viennent d'un outil (objectif : tous) et la précision du contexte par régime.

### BTP — le contrat spécifique devant le modèle générique

Un contrôleur de factures d'un groupe de construction qui mène de grands chantiers à Dubaï demande : « Quelle retenue de garantie appliquer à la facture du lot électricité ? ». La base contient le modèle générique de sous-traitance (retenue de 5 %, note 0 pour cette question), le contrat du lot électricité (retenue de 10 %, note 3), la règle de TVA de 5 % (note 1), et des morceaux sur le lot plomberie, la validation des situations et le planning. BM25 place le modèle générique en tête, et un agent qui lirait seulement le premier résultat de BM25 appliquerait 5 % au lieu de 10 % : son rang réciproque serait de 0,5. Le cosinus place le contrat en tête, et la fusion lui donne la première place avec 0,032522 contre 0,032266 (point 1 de la démonstration) : rang réciproque 1, NDCG@3 0,917, Recall@3 0,5 puisque la règle de TVA n'est pas dans le top-3. La réponse cite `[btp-02]` pour la retenue de 10 % libérée à la réception, elle est étayée, et l'agent répond. Une retenue mal calculée fausse le montant payé au sous-traitant et doit ensuite être régularisée, avec la TVA de 5 % qui s'applique à la facture. On suit le MRR@1 par lot et la part des factures validées avec la clause du contrat spécifique.

### Secteur public — l'arabe normalisé, et une question hors corpus

Une entité de services publics en ligne, accessible par UAE Pass, reçoit d'abord une requête mixte : « بطاقه الهويه الاماراتيه renewal », écrite avec un ha à la place de la ta marbuta et un alef sans hamza. La page arabe sur le renouvellement de la carte d'identité émiratie est écrite correctement : sans normalisation, aucun mot ne correspond et son score BM25 vaut 0 ; avec la normalisation, il vaut 3,69, et BM25 ramène la page arabe puis la page anglaise. La fusion donne `pub-01`, `pub-02`, `pub-03`, avec un Recall@3, un rang réciproque et un NDCG@3 de 1, et la réponse en anglais qui cite les deux pages est étayée. La seconde question, « How do I get a fishing permit? », porte sur une démarche absente du corpus : aucun mot ne correspond, le meilleur cosinus vaut 0,06, sous le seuil de 0,5, et l'agent s'abstient en orientant l'usager vers un agent humain au lieu d'improviser une procédure à partir de trois pages sans rapport. Ses métriques de classement sont indéfinies, et elle est évaluée par le test d'abstention, réussi ici (1 sur 1). Un service public doit répondre aussi bien en arabe qu'en anglais, et son corpus ne contient que des pages publiques, sans donnée personnelle d'usager. On suit le taux d'abstention sur un jeu de questions hors périmètre et les métriques de classement séparément par langue.

## Pièges et limites

- **Prendre les vecteurs jouets pour des embeddings.** Un vrai modèle produit des cosinus d'une autre échelle, souvent tous élevés : le seuil d'abstention de 0,5 n'a de sens que pour ces vecteurs, et il se recalibre sur des questions hors sujet réelles.
- **Faire de la fidélité approchée le seul garde-fou.** Elle laisse passer un bon nombre mal attribué et rejette une bonne paraphrase (démonstration, point 3). C'est un filet rapide et gratuit, à compléter par la Faithfulness de l'étape 54.
- **Tirer des conclusions de corpus minuscules.** Avec cinq à sept morceaux, l'IDF de BM25 change beaucoup pour un seul mot, et deux morceaux de même score sont départagés par leur identifiant : les égalités de la RRF devraient plutôt l'être par un autre signal, par exemple le cosinus.
- **Confondre ce que l'agent voit et ce que l'évaluation sait.** En ligne, l'agent ne connaît que les cosinus, ses sources et sa réponse ; le Recall@k, le MRR et le NDCG exigent des jugements de pertinence et ne se calculent que sur un jeu annoté.
- **Oublier de citer les outils.** Un nombre calculé sans source citée est indiscernable d'une hallucination : tout calcul passe par un outil dont le résultat devient une source.

### Exercice feuille blanche

1. Sans regarder le code, écrire `fidelite_approchee` avec ses trois conditions, puis vérifier que la réponse du cas assurance obtient 0,5.
2. Prédire, puis vérifier : dans le cas BTP, avec k = 2 au lieu de 3, que valent le Recall@k, le rang réciproque et le NDCG@k ? (Réponse : rien ne change, 0,5 ; 1 ; 0,917, parce que le morceau du rang 3, `btp-06`, n'est pas pertinent et que l'IDCG ne compte que les notes 3 et 1.)
3. Trouver le bug : on retire le filtre `if bm25[d] > 0` dans `rechercher`. Que devient le top-3 de la question sur le permis de pêche ? (Réponse : `pub-01`, `pub-04`, `pub-02`. Tous les scores BM25 étant nuls, le classement BM25 suit l'ordre alphabétique des identifiants, et `pub-01` gagne une place sans contenir un seul mot de la question.)

> Suite : [Applications du RAG par domaine](<30-RAG-Applications-Domaines.md>) — étape 30.
