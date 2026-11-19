# Récapitulatif — cartes, processus, synthèse

Les images de ce dossier sont des affiches de révision. Chacune a sa fiche du même nom : l'image à gauche, la fiche à droite. Si une affiche déforme un accent ou une formule, la fiche fait foi.

L'ordre n'est pas celui d'un manuel qui rangerait l'algèbre avant tout le reste. C'est l'ordre de construction de ce parcours : chaque formule est placée juste avant la première chose qui s'en sert, le même ordre que les dossiers `01-Agent` à `13-Projet-Final` et que les douze paliers de `Exercices/`. L'index de révision `14-Synthese-et-Revision/79-Index-des-Equations.md` regroupe autrement, pour réviser ; il ne remplace pas cet ordre.

Deux chronologies coexistent. Il ne faut pas les mélanger.

- **Construction** : l'ordre dans lequel on écrit l'agent. C'est celui des diagrammes de classes de ce dossier.
- **Requête** : l'ordre dans lequel une demande traverse un agent déjà écrit. Le parcours le fixe ainsi : prompt, schéma, outil, boucle, mémoire et RAG, attention, plan, orchestration, MCP, évaluation, garde-fou.

## Les affiches

| Image | Fiche | Ce qu'elle fixe |
| --- | --- | --- |
| `01_carte_mentale_creation.jpg` | [fiche](<01_carte_mentale_creation.md>) | Les huit moments de la construction, du centre vers les branches, dans le sens des aiguilles. |
| `02_processus_vertical_fondations.jpg` | [fiche](<02_processus_vertical_fondations.md>) | Classes 1 à 6 : espérance, fiabilité, softmax, vraisemblance, budget, vecteurs. |
| `03_processus_vertical_recherche.jpg` | [fiche](<03_processus_vertical_recherche.md>) | Classes 7 à 12 : mémoire, BM25, RRF, rappel et précision, MRR et NDCG, attention. |
| `04_processus_vertical_decision.jpg` | [fiche](<04_processus_vertical_decision.md>) | Classes 13 à 18 : position, décision, information, mesure, coût, apprentissage. |
| `05_carte_mentale_justifications.jpg` | [fiche](<05_carte_mentale_justifications.md>) | Pourquoi aucune de ces formules ne peut passer avant celle dont elle dépend. |
| `06_synthese.jpg` | [fiche](<06_synthese.md>) | La chaîne en neuf phrases. |
| `07_resume.jpg` | [fiche](<07_resume.md>) | Les deux ordres, construction et requête, sur une seule affiche. |
| `08_bilan.jpg` | [fiche](<08_bilan.md>) | Ce qu'il reste quand les formules sont en place. |

On lit `01`, puis `02`, `03`, `04` de haut en bas, puis `05`, puis `06`, `07`, `08`. Les affiches `09` à `45` reprennent ensuite une formule ou une carte à la fois. Leur texte exact, celui qui fait foi si l'image déforme un signe, est dans [09_Affiches-unitaires.md](<09_Affiches-unitaires.md>).

## Les dix-huit classes, dans l'ordre

Chaque classe reprend une formule déjà démontrée dans `Images/`. Le numéro d'étape est celui du parcours.

### 1. Espérance — étape 1

$$
\mathbb{E}[X] = \sum_i x_i \, P(x_i)
$$

Prévoir un coût ou un gain moyen, en comptant les branches rares. L'utilité espérée et Bellman ne sont que cette somme, écrite plus tard avec d'autres noms. Fiche image : [22](<../06-Decision/22_esperance.md>).

### 2. Fiabilité en série — étape 1

$$
P(\text{succès}) = \prod_{i=1}^{n} p_i
$$

L'agent ne va au bout que si toutes ses étapes réussissent. Chaque pᵢ est au plus 1, donc ajouter une étape ne relève jamais la fiabilité. Fiche : [29](<../01-Introduction/29_fiabilite_serie.md>).

### 3. Softmax et température — étape 2

$$
P(i) = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
$$

Les logits deviennent une loi sur le prochain token. T → 0 n'est pas une softmax : c'est un argmax. On la lit avant les prompts, parce qu'un prompt juge des tokens qui sortent d'ici. Fiche : [04](<../03-Modele/04_softmax_temperature.md>).

### 4. Vraisemblance autorégressive — étape 3

$$
P(x_1,\ldots,x_n) = \prod_{t=1}^{n} P(x_t \mid x_{<t})
$$

La phrase entière est le produit des choix de la softmax. Fiche : [23](<../03-Modele/23_vraisemblance_autoregressive.md>).

### 5. Budget de contexte — étape 13 ter

On décide ce qui a le droit d'entrer dans la fenêtre avant de la remplir. Un agent qui empile tout paie ensuite un coût qui croît comme un carré du nombre d'étapes. Fiche : [15](<../05-Contexte/15_budget_contexte.md>).

### 6. Produit scalaire, norme L2, cosinus — étape 14

$$
x^\top y = \sum_{i=1}^{d} x_i y_i
\qquad
\|x\|_2 = \sqrt{\sum_i x_i^2}
\qquad
\cos(x,y) = \frac{x^\top y}{\|x\|_2 \, \|y\|_2}
$$

Une seule fois, avant la mémoire et avant le RAG : les deux comparent des vecteurs. Le cosinus compare la direction, pas la longueur. Vecteur nul : on refuse, on n'ajoute pas un epsilon. Fiches : [01](<../02-Vecteurs/01_produit_scalaire.md>), [02](<../02-Vecteurs/02_norme_L2.md>), [03](<../02-Vecteurs/03_similarite_cosinus.md>).

### 7. Score de mémoire — étapes 16 et 17

$$
rec_j = e^{-\lambda \Delta t_j} = 2^{-\Delta t_j / t_{1/2}}
\qquad
\lambda = \frac{\ln 2}{t_{1/2}}
$$

$$
score_j = w_{sim}\,\widetilde{sim}_j + w_{rec}\,\widetilde{rec}_j + w_{imp}\,\widetilde{imp}_j
$$

Poids positifs, somme 1. Chaque composante est ramenée dans [0, 1] par min-max sur les candidats du moment. La similarité est le cosinus de l'étape 14. Fiche : [27](<../05-Contexte/27_score_memoire.md>).

### 8. TF-IDF, puis BM25 — étape 22

Le sens vectoriel rate un numéro de clause ou un identifiant. BM25 classe par les mots exacts. TF-IDF est l'ancêtre lu dans la même étape : un mot rare pèse plus qu'un mot partout. Fiches : [24](<../04-Recherche/24_tfidf.md>), [11](<../04-Recherche/11_bm25.md>).

### 9. Fusion RRF — étape 24

$$
\mathrm{RRF}(d) = \sum_{r \ni d} \frac{1}{k_{RRF} + \mathrm{rang}_r(d)}
\qquad
k_{RRF} = 60
$$

Le score hybride de l'étape 23 mélange cosinus et BM25, qui n'ont pas la même échelle. RRF n'utilise que les rangs. Il vient donc après les deux classements, pas avant. Fiche : [25](<../04-Recherche/25_rrf.md>).

### 10. Rappel@k et précision@k — étapes 25 et 26

$$
\mathrm{Rappel@}k = \frac{\text{documents utiles retrouvés dans le top }k}{\text{documents utiles}}
\qquad
\mathrm{Précision@}k = \frac{\text{documents utiles dans le top }k}{k}
$$

Le rappel dit quelles preuves manquent. La précision dit combien de résultats sont utiles. On les calcule avant de faire confiance au classement. Fiches : [13](<../04-Recherche/13_rappel.md>), [12](<../04-Recherche/12_precision.md>).

### 11. MRR et NDCG — étapes 27 et 28

Le MRR dit à quel rang tombe le premier document utile. Le NDCG dit qu'un bon document en position 1 vaut plus qu'en position 10. Fiches : [33](<../04-Recherche/33_mrr.md>), [26](<../04-Recherche/26_ndcg.md>).

### 12. Attention — étape 31

$$
\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right) V
$$

Le RAG a déjà gonflé le prompt. L'attention décide quels tokens de ce prompt pèsent sur le token en cours. La diviser par √dₖ empêche le produit scalaire de saturer la softmax. Fiche : [05](<../03-Modele/05_attention_scaled_dot_product.md>).

### 13. Encodage de position — étape 35

$$
PE_{(pos, 2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right)
\qquad
PE_{(pos, 2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)
$$

Sans position, l'attention ne distingue pas l'ordre des mots. Elle vient donc après l'attention, pas avant. Fiche : [30](<../03-Modele/30_encodage_position.md>).

### 14. Utilité, Bellman, Q, REINFORCE — étape 38

$$
EU(a) = \sum_o P(o \mid a)\, U(o)
$$

$$
V^{*}(s) = \max_a \sum_{s'} \mathcal{P}(s' \mid s, a)\, \big[ \mathcal{R}(s,a,s') + \gamma V^{*}(s') \big]
$$

L'utilité espérée choisit une action. Bellman y ajoute la suite, actualisée par γ. Q* est la valeur d'une action ; la politique gloutonne prend l'argmax. Q-learning estime Q par l'expérience. REINFORCE monte le gradient de la politique : il apprend ce que Bellman décrit, il ne le remplace pas. A* (f = g + h, étape 40) vient ensuite seulement : ce nombre ne dit pas si l'étape vaut le coup sous incertitude. Fiches : [10](<../06-Decision/10_utilite_esperee.md>), [09](<../06-Decision/09_equation_bellman.md>), [18](<../06-Decision/18_q_learning.md>), [19](<../06-Decision/19_reinforce.md>).

### 15. Valeur de l'information — étape 38

On cherche, ou on appelle un outil de plus, seulement si le gain espéré dépasse le coût. C'est le critère d'arrêt : une boucle dont la valeur marginale devient négative s'arrête. Fiche : [28](<../06-Decision/28_valeur_information.md>).

### 16. Mesure — étapes 50 à 52

$$
F_1 = \frac{2PR}{P+R}
\qquad
D_{KL}(P \parallel Q) = \sum_i P(i) \log \frac{P(i)}{Q(i)}
$$

$$
P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}
\qquad
\mathrm{Brier} = \frac{1}{N}\sum_n (p_n - o_n)^2
$$

$$
H = -\sum_i p_i \log p_i
\qquad
\mathrm{PPL} = \exp(\text{entropie croisée})
$$

La précision, le rappel et le F1 généraux ouvrent l'évaluation ; les variantes (contexte, appels d'outils) en sont des cas. La KL mesure un écart de lois, notamment quand un garde-fou ou un alignement compare deux distributions. Bayes remet une alerte à l'échelle du taux de base. Brier juge une probabilité, pas une étiquette. L'entropie mesure la dispersion ; la perplexité, à quel point le modèle est surpris par le token réel. Le score de risque (étape 67) vient après : il lit ces signaux, par exemple sous ces trois formes :

$$
u = 1 - F
\qquad
u = 1 - \frac{1}{\mathrm{PPL}}
\qquad
u = 1 - e^{-D_{KL}}
$$

Fiches : [14](<../04-Recherche/14_score_f1.md>), [17](<../07-Mesure/17_divergence_kl.md>), [07](<../07-Mesure/07_theoreme_bayes.md>), [20](<../07-Mesure/20_score_brier.md>), [21](<../07-Mesure/21_entropie.md>), [06](<../03-Modele/06_entropie_croisee.md>), [32](<../03-Modele/32_perplexite.md>).

### 17. Coût d'inférence — étape 72

$$
\text{Coût} = N_{in} P_{in} + N_{out} P_{out}
$$

Le prix d'un appel est linéaire. Sans élagage, l'étape k relit tout l'historique et le total d'entrée croît comme K². On chiffre le service quand la boucle existe vraiment. Fiche : [16](<../09-Production/16_cout_inference.md>).

### 18. Gradient, descente, Adam — étapes 73 et 74

$$
\nabla_\theta L
\qquad
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y}\frac{\partial y}{\partial x}
\qquad
\theta \leftarrow \theta - \eta \nabla_\theta L
$$

La règle de la chaîne propage la perte. La descente marche à l'opposé du gradient. Adam donne un pas différent à chaque poids, parce que le même η ne convient pas à tous. On spécialise le modèle seulement quand l'agent sait déjà percevoir, décider et s'arrêter. Fiches : [34](<../08-Entrainement/34_gradient.md>), [08](<../08-Entrainement/08_descente_de_gradient.md>), [31](<../08-Entrainement/31_adam.md>).

L'étape 77 n'ajoute pas de formule. Elle assemble celles-ci dans un seul programme.

## Ce que cet ordre refuse

- Mettre l'attention au début. Elle répond à une question qu'on ne se pose qu'une fois le contexte construit.
- Fusionner BM25 et cosinus par une moyenne de scores. Les unités diffèrent ; RRF additionne des rangs.
- Placer le garde-fou avant l'évaluation. Il consomme la fidélité, la perplexité et la KL.
- Lancer Adam avant que la boucle de l'étape 1 existe.
- Confondre l'ordre de construction avec l'ordre d'une requête. Le second décrit un agent déjà écrit.
