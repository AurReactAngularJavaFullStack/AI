# Étape 38 — Processus de Décision Markovien (MDP) et Équation de Bellman

> Étape 38 du parcours · Prérequis : [Planification : définitions fondamentales](<37b-Planification-Definitions-Fondamentaux.md>) · Suite : [Bellman et contraction, seconde moitié des fondements](<../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>)

**Dossier :** 07-Planification  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, Product Engineers, Forward-Deployed Engineers  
**Nom du fichier :** 38-Agent-et-Planification-MDP-Bellman.md

## Définition

Un MDP (Markov Decision Process, processus de décision markovien) est un modèle de décision en plusieurs pas. À chaque pas, l'agent est dans un état s, choisit une action a, reçoit une récompense R et passe dans un état suivant s′, tiré au hasard selon des probabilités connues 𝒫(s′ ∣ s, a). Un MDP est défini par cinq éléments : les états 𝒮, les actions 𝒜, les probabilités de transition 𝒫, les récompenses ℛ et le facteur d'actualisation γ. « Markovien » veut dire que la loi de l'état suivant ne dépend que de l'état et de l'action présents, pas du chemin qui y a mené : tout ce qui compte pour la suite doit donc être écrit dans l'état. La **valeur** d'un état est la somme actualisée espérée des récompenses futures quand on part de cet état : une récompense qui arrive k pas plus tard est multipliée par γᵏ, puis on fait la moyenne sur tous les futurs possibles. L'équation de Bellman écrit cette valeur de façon récursive : la valeur d'un état est la récompense immédiate espérée, plus γ fois la valeur espérée de l'état suivant.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, Bellman sert au moment de **décider**, dans le planificateur. Quand une action a des conséquences qui s'étalent dans le temps (réserver maintenant ou attendre, poser une question de clarification ou répondre, escalader ou surveiller), l'agent compare les actions par leur valeur Q(s, a), et non par leur seule récompense immédiate. Comme le dit l'étape 37 bis, un modèle de langage ne résout pas lui-même une équation de Bellman : on la résout dans un **outil déterministe** que le plan appelle, sur un petit MDP dont l'équipe métier écrit les états, les actions, les probabilités et les récompenses. La même idée est au cœur des recherches arborescentes utilisées avec les LLM (Tree of Thoughts, MCTS), où un évaluateur estime la valeur d'un chemin de raisonnement avant de le poursuivre.

## Équation complète

Retour, c'est-à-dire gain cumulé actualisé, à partir du temps t :

$$
G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1} = R_{t+1} + \gamma\, G_{t+1}
$$

Valeur d'un état sous une politique π, forme compacte :

$$
V^\pi(s) = \mathbb{E}_\pi \left[ R_{t+1} + \gamma V^\pi(S_{t+1}) \mid S_t = s \right]
$$

Équation d'**évaluation** de Bellman, forme développée (une moyenne sur les actions, pondérée par π) :

$$
V^\pi(s) = \sum_{a \in \mathcal{A}} \pi(a \mid s) \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^\pi(s') \right]
$$

Équation d'**optimalité** de Bellman (un maximum sur les actions) :

$$
V^{*}(s) = \max_{a \in \mathcal{A}} \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^{*}(s') \right]
$$

Valeur d'une action, et politique gloutonne qui en découle :

$$
Q^{*}(s, a) = \sum_{s'} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^{*}(s') \right] , \qquad \pi^{*}(s) = \arg\max_{a} Q^{*}(s, a)
$$

Itération de valeur, l'algorithme du code :

$$
V_{k+1} = \mathcal{T}^{*} V_k , \qquad (\mathcal{T}^{*} V)(s) = \max_{a} \sum_{s'} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V(s') \right]
$$

## Décryptage des symboles

$$
s,\; s'
$$

**Sens :** l'état présent et l'état suivant (« recherche de vol », « vol direct pris ») · **Type / plage :** élément de l'ensemble fini 𝒮 · **Variable Python :** `etat`, `suivant` (entiers de 0 à 4)

$$
a
$$

**Sens :** une action possible dans l'état s (« pas_cher », « direct », « hotel ») · **Type / plage :** élément de 𝒜 · **Variable Python :** `action`

$$
\mathcal{P}(s' \mid s, a)
$$

**Sens :** probabilité d'arriver en s′ quand on fait a dans s ; pour chaque couple (s, a), ces probabilités somment à 1 · **Type / plage :** réel dans [0, 1] · **Variable Python :** `proba`, premier élément de chaque triplet de `TRANSITIONS`

$$
\mathcal{R}(s, a, s'),\; R_{t+1}
$$

**Sens :** récompense reçue en passant de s à s′ par a ; Rₜ₊₁ est celle qui est reçue juste après le temps t · **Type / plage :** réel, borné en valeur absolue par Rₘₐₓ · **Variable Python :** `recompense`

$$
\gamma
$$

**Sens :** facteur d'actualisation : une récompense reçue k pas plus tard compte γᵏ fois · **Type / plage :** réel dans [0, 1[ ; γ = 1 n'est permis que si chaque épisode se termine · **Variable Python :** `gamma`

$$
G_t
$$

**Sens :** retour : somme actualisée des récompenses à partir du temps t, sur une trajectoire donnée · **Type / plage :** réel aléatoire · **Variable Python :** non stocké, le code manipule directement sa moyenne V

$$
\pi(a \mid s)
$$

**Sens :** politique : probabilité que l'agent choisisse a dans l'état s ; une politique déterministe met toute la probabilité sur une seule action · **Type / plage :** réel dans [0, 1], de somme 1 sur les actions · **Variable Python :** `pi[etat][action]` pour l'évaluation, `politique[etat]` pour la politique gloutonne

$$
\mathbb{E}_\pi
$$

**Sens :** espérance quand l'agent suit π : la moyenne de tous les futurs possibles, chacun pondéré par sa probabilité · **Type / plage :** opérateur · **Variable Python :** la boucle `for proba, recompense, suivant in ...` qui additionne des `proba * (...)`

$$
V^\pi(s)
$$

**Sens :** valeur de l'état s sous π : la somme actualisée **espérée** des récompenses futures, et non une « récompense totale » · **Type / plage :** réel, |V| ≤ Rₘₐₓ / (1 − γ) · **Variable Python :** `evaluation_politique(pi, gamma)[etat]`

$$
V^{*}(s),\; Q^{*}(s, a)
$$

**Sens :** la meilleure valeur atteignable depuis s, et la valeur de l'action a dans s quand on joue au mieux ensuite · **Type / plage :** réels · **Variable Python :** `iteration_valeur(gamma)[0][etat]`, `backup_action(V, etat, action, gamma)`

$$
\mathcal{T}^{*}
$$

**Sens :** opérateur de Bellman : il prend une estimation V et rend une estimation meilleure, en faisant une sauvegarde (un « backup ») dans chaque état · **Type / plage :** fonction qui envoie un vecteur de |𝒮| valeurs sur un autre · **Variable Python :** `T_etoile(V, gamma)`

$$
\lVert U - V \rVert_\infty = \max_{s} \lvert U(s) - V(s) \rvert
$$

**Sens :** norme infinie : le plus grand écart entre deux estimations, état par état · **Type / plage :** réel ≥ 0 · **Variable Python :** `norme_inf(U, V)`

## Démonstration

### 1. Le retour se replie sur lui-même

On écrit le retour terme à terme, puis on met γ en facteur dans tous les termes sauf le premier :

$$
G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \dots = R_{t+1} + \gamma \left( R_{t+2} + \gamma R_{t+3} + \dots \right) = R_{t+1} + \gamma\, G_{t+1}
$$

La parenthèse est exactement le retour à partir du temps t + 1, parce qu'elle a la même forme, décalée d'un pas. La somme infinie a bien un sens : si toutes les récompenses vérifient |R| ≤ Rₘₐₓ et si γ < 1, elle est dominée par la série géométrique Rₘₐₓ (1 + γ + γ² + …), qui converge (point 6). Si chaque épisode se termine en un nombre fini de pas, comme dans l'exemple du vol, la somme est finie et γ = 1 est permis.

### 2. L'équation d'évaluation : V^π est une moyenne pondérée par π

Par définition, la valeur est l'espérance du retour :

$$
V^\pi(s) = \mathbb{E}_\pi \left[ G_t \mid S_t = s \right] = \mathbb{E}_\pi \left[ R_{t+1} \mid S_t = s \right] + \gamma\, \mathbb{E}_\pi \left[ G_{t+1} \mid S_t = s \right]
$$

On passe de la première écriture à la seconde parce que Gₜ = Rₜ₊₁ + γ Gₜ₊₁ (point 1) et que l'espérance d'une somme est la somme des espérances. On calcule ensuite chaque terme en conditionnant d'abord sur l'action Aₜ = a, tirée avec la probabilité π(a ∣ s), puis sur l'état suivant Sₜ₊₁ = s′, tiré avec la probabilité 𝒫(s′ ∣ s, a) : c'est la loi de l'espérance totale. Il reste à remplacer l'espérance du retour futur quand s′ est connu :

$$
\mathbb{E}_\pi \left[ G_{t+1} \mid S_t = s,\, A_t = a,\, S_{t+1} = s' \right] = \mathbb{E}_\pi \left[ G_{t+1} \mid S_{t+1} = s' \right] = V^\pi(s')
$$

La première égalité est la propriété de Markov : une fois s′ connu, le passé (s et a) n'apporte plus aucune information sur la suite, parce que les transitions futures ne dépendent que de l'état présent et que π ne change pas avec le temps. La seconde égalité est la définition de V^π en s′. En regroupant les deux termes sous les mêmes sommes, on obtient l'équation d'évaluation :

$$
V^\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s'} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^\pi(s') \right]
$$

On note 𝒯^π l'opérateur qui applique ce membre de droite à une estimation V quelconque. L'équation dit que V^π est un point fixe de 𝒯^π.

### 3. L'opérateur de Bellman est une contraction de rapport γ

**Lemme.** Pour deux fonctions f et g définies sur le même ensemble fini d'actions :

$$
\left| \max_a f(a) - \max_a g(a) \right| \le \max_a \left| f(a) - g(a) \right|
$$

Preuve : soit a₁ une action qui maximise f. Alors max f − max g ≤ f(a₁) − g(a₁), parce que max g ≥ g(a₁) ; et f(a₁) − g(a₁) ≤ max |f − g|. Le même raisonnement, avec une action qui maximise g, borne max g − max f. Les deux bornes ensemble donnent la valeur absolue.

**Théorème.** Pour deux estimations quelconques U et V :

$$
\lVert \mathcal{T}^{*} U - \mathcal{T}^{*} V \rVert_\infty \le \gamma \lVert U - V \rVert_\infty
$$

Preuve : on fixe un état s et on applique le lemme aux deux fonctions qui, à une action a, associent la somme de Bellman calculée avec U, puis avec V. Les récompenses s'annulent dans la différence :

$$
\left| (\mathcal{T}^{*} U)(s) - (\mathcal{T}^{*} V)(s) \right| \le \max_a \gamma \left| \sum_{s'} \mathcal{P}(s' \mid s, a) \big( U(s') - V(s') \big) \right| \le \gamma \max_a \sum_{s'} \mathcal{P}(s' \mid s, a) \lVert U - V \rVert_\infty = \gamma \lVert U - V \rVert_\infty
$$

La deuxième inégalité vient de ce que la valeur absolue d'une somme est au plus la somme des valeurs absolues, et que chaque |U(s′) − V(s′)| est au plus le plus grand écart. La dernière égalité vient de ce que les probabilités somment à 1. Comme la borne vaut pour chaque s, elle vaut pour le maximum sur s. Le même calcul, sans le lemme, montre que 𝒯^π est aussi une contraction de rapport γ : une moyenne pondérée par π ne peut pas agrandir un écart.

### 4. Point fixe unique, convergence, et ce que vaut le critère d'arrêt

**Unicité.** Si V et W sont deux points fixes de 𝒯\*, alors ‖V − W‖∞ = ‖𝒯\*V − 𝒯\*W‖∞ ≤ γ ‖V − W‖∞. Avec γ < 1, ce n'est possible que si ‖V − W‖∞ = 0 : il y a au plus un point fixe.

**Existence et convergence.** On part de n'importe quel V₀ et l'on pose Vₖ₊₁ = 𝒯\*Vₖ. En appliquant la contraction k fois, ‖Vₖ₊₁ − Vₖ‖∞ ≤ γᵏ ‖V₁ − V₀‖∞. Pour m > k, l'inégalité triangulaire et la série géométrique donnent :

$$
\lVert V_m - V_k \rVert_\infty \le \left( \gamma^k + \gamma^{k+1} + \dots + \gamma^{m-1} \right) \lVert V_1 - V_0 \rVert_\infty \le \frac{\gamma^k}{1-\gamma} \lVert V_1 - V_0 \rVert_\infty
$$

Ce majorant tend vers 0 : la suite est de Cauchy, donc elle converge vers une limite, que l'on note V\*, parce qu'un espace de dimension finie est complet. Comme 𝒯\* est continu (une contraction l'est), passer à la limite dans Vₖ₊₁ = 𝒯\*Vₖ donne 𝒯\*V\* = V\*. C'est le théorème du point fixe de Banach, démontré ici dans le cas qui nous sert. La vitesse se lit directement :

$$
\lVert V_k - V^{*} \rVert_\infty = \lVert \mathcal{T}^{*} V_{k-1} - \mathcal{T}^{*} V^{*} \rVert_\infty \le \gamma \lVert V_{k-1} - V^{*} \rVert_\infty \le \dots \le \gamma^k \lVert V_0 - V^{*} \rVert_\infty
$$

**Le critère d'arrêt.** Le code s'arrête quand l'écart entre deux tours passe sous un seuil ε. Cela ne veut pas dire que l'erreur est sous ε. On écrit ‖Vₖ₊₁ − V\*‖ ≤ γ ‖Vₖ − V\*‖ ≤ γ (‖Vₖ − Vₖ₊₁‖ + ‖Vₖ₊₁ − V\*‖), puis on regroupe les termes en ‖Vₖ₊₁ − V\*‖ du même côté :

$$
\lVert V_{k+1} - V^{*} \rVert_\infty \le \frac{\gamma}{1-\gamma} \lVert V_{k+1} - V_k \rVert_\infty
$$

À γ = 0,95, le facteur vaut 19 : un écart de 0,01 garantit seulement une erreur inférieure à 0,19. Le programme montre que cette borne est atteinte.

### 5. L'équation d'optimalité, et pourquoi la politique gloutonne est la meilleure

On appelle V\* le point fixe unique de 𝒯\*. Il reste à montrer qu'il mérite son nom : aucune politique ne fait mieux, et une politique l'atteint.

**Toute politique fait au plus V\*.** Pour toute estimation V, on a 𝒯^π V ≤ 𝒯\*V état par état, parce qu'une moyenne pondérée de nombres est au plus leur maximum. De plus, 𝒯\* est croissant : si U ≤ V partout, alors 𝒯\*U ≤ 𝒯\*V, parce que γ ≥ 0 et que les probabilités sont positives. Donc V^π = 𝒯^π V^π ≤ 𝒯\*V^π ≤ 𝒯\*(𝒯\*V^π) ≤ …, et cette suite croissante converge vers V\* (point 4). Ainsi V^π ≤ V\* pour toute politique π.

**La politique gloutonne atteint V\*.** Soit π\* la politique qui choisit, dans chaque état, une action de plus grand Q\*(s, a). Appliquer à V\* l'opérateur d'évaluation de π\* revient à prendre ce maximum, donc donne 𝒯\*V\* = V\*. Ainsi V\* est un point fixe de l'opérateur d'évaluation de π\*. Cet opérateur est une contraction (point 3) et n'a donc qu'un point fixe, la valeur de π\*. La valeur de π\* est donc V\*.

Conclusion : V\*(s) est la plus grande valeur atteignable depuis s, elle vérifie l'équation d'optimalité, et il suffit de la connaître pour agir au mieux, en prenant l'argmax de Q\*. Le code fait exactement cela : il calcule V\* par itération de valeur, puis lit la politique gloutonne. La fonction `evaluation_politique` calcule à part V^π pour une politique donnée.

### 6. Borne des valeurs et horizon effectif

Si |R| ≤ Rₘₐₓ à chaque pas, la série géométrique borne toute valeur :

$$
\lvert V^\pi(s) \rvert \le \sum_{k=0}^{\infty} \gamma^k R_{\max} = \frac{R_{\max}}{1-\gamma}
$$

La borne est atteinte par un état qui rapporte Rₘₐₓ à chaque pas et ne s'arrête jamais : avec Rₘₐₓ = 1 et γ = 0,95, sa valeur vaut 1 / 0,05 = 20. On lit donc 1 / (1 − γ) comme un **horizon effectif** : la valeur se comporte comme une somme sur environ 1 / (1 − γ) pas. Un calcul précis justifie ce nombre. Comme ln x ≤ x − 1 pour tout x > 0, on a ln γ ≤ −(1 − γ), donc :

$$
\gamma^{1/(1-\gamma)} = e^{\ln \gamma / (1-\gamma)} \le e^{-1} \approx 0{,}368
$$

Une récompense placée à 1 / (1 − γ) pas pèse donc au plus 37 % de son montant. À γ = 0,95, l'horizon vaut 20 pas et 0,95²⁰ ≈ 0,358. À γ = 0,10, il vaut 1,1 pas : l'agent est myope. À γ = 0,99, il vaut 100 pas.

### 7. Exemple fait à la main (le code reprend ces nombres)

Le MDP du vol. Depuis « recherche », l'action « pas cher » rapporte +30 et mène à « vol pas cher pris », où l'hôtel rapporte −20 et mène à « utilisateur épuisé » (état final). L'action « direct » rapporte +5 et mène à « vol direct pris », où l'hôtel rapporte +80 et mène à « utilisateur content » (état final). Les états finaux valent 0. Les deux états intermédiaires n'ont qu'une action, donc V\*(vol pas cher pris) = −20 et V\*(vol direct pris) = 80, quel que soit γ.

| γ | Q\*(recherche, pas cher) | Q\*(recherche, direct) | Action choisie |
|---|---|---|---|
| 0,10 | 30 + 0,10 × (−20) = 28 | 5 + 0,10 × 80 = 13 | pas cher |
| 0,25 | 30 + 0,25 × (−20) = 25 | 5 + 0,25 × 80 = 25 | égalité : la première action écrite reste |
| 0,95 | 30 + 0,95 × (−20) = 11 | 5 + 0,95 × 80 = 81 | direct |

Le seuil de bascule s'obtient en égalant les deux valeurs :

$$
30 - 20\gamma = 5 + 80\gamma \;\Longleftrightarrow\; 25 = 100\gamma \;\Longleftrightarrow\; \gamma = 0{,}25
$$

Sous 0,25, le vol pas cher gagne ; au-dessus, le vol direct gagne.

**Évaluer n'est pas optimiser.** Une politique qui tire « pas cher » ou « direct » à pile ou face vaut, à γ = 0,95, la moyenne des deux valeurs d'action :

$$
V^\pi(\text{recherche}) = 0{,}5 \times 11 + 0{,}5 \times 81 = 46 \le V^{*}(\text{recherche}) = 81
$$

**L'espérance additionne les branches.** Si le vol pas cher est annulé dans 20 % des cas (récompense −50, état final), sa valeur à γ = 0,95 vaut :

$$
0{,}80 \times \big(30 + 0{,}95 \times (-20)\big) + 0{,}20 \times \big(-50 + 0{,}95 \times 0\big) = 0{,}80 \times 11 - 10 = 8{,}8 - 10 = -1{,}2
$$

L'agent ne retient pas la branche à +30. Il retient −1,2, parce que l'équation pondère chaque branche par sa probabilité.

**La contraction sur cet exemple.** Avec U = [0, 0, 0, 0, 0] et W = [0, 10, 10, 0, 0], l'écart vaut 10. Après une sauvegarde à γ = 0,95, on obtient 𝒯\*U = [30, −20, 80, 0, 0] et 𝒯\*W = [39,5, −20, 80, 0, 0] : l'écart vaut 9,5 = 0,95 × 10. La borne du point 3 est atteinte.

## Effets et comportement

- **γ proche de 0 : l'agent devient myope.** Il ne regarde que la récompense immédiate (horizon effectif d'environ 1 pas) et prend le vol pas cher, comme un agent qui clique sur un lien sponsorisé pour un gain immédiat au lieu de chercher la vraie réponse.
- **γ proche de 1 : l'agent devient prévoyant, mais la convergence ralentit.** L'erreur ne baisse que d'un facteur γ par tour : il faut environ ln(ε / ‖V₀ − V\*‖) / ln γ tours, soit 149 tours pour passer sous 0,01 dans l'exemple de la veille à γ = 0,95. Les valeurs grandissent aussi, jusqu'à Rₘₐₓ / (1 − γ).
- **Augmenter une récompense immédiate augmente la valeur de l'action**, à valeurs futures fixées, d'exactement ce montant multiplié par la probabilité de la branche. Cela peut faire basculer l'argmax, donc la politique, et rendre l'agent plus enclin à choisir cette action.
- **Dans un MDP sans cycle, où chaque épisode finit, l'itération de valeur devient exacte** après un nombre de tours égal à la profondeur du graphe, plus un tour pour constater que rien ne bouge : 3 tours ici, quel que soit γ.

## Du symbole au code Python

| Symbole | Variable ou fonction Python |
|---|---|
| s, s′ | `etat`, `suivant` (constantes `RECHERCHE`, `APRES_PAS_CHER`, …) |
| 𝒫(s′ ∣ s, a) et ℛ(s, a, s′) | triplets `(proba, recompense, suivant)` de `TRANSITIONS[etat][action]` |
| γ | `gamma` |
| Q(s, a) | `backup_action(V, etat, action, gamma)` |
| 𝒯\* et l'argmax | `T_etoile(V, gamma)`, qui renvoie `(nouveau, politique)` |
| ‖U − V‖∞ | `norme_inf(U, V)` |
| V\* par itération de valeur | `iteration_valeur(gamma)` |
| V^π par itération de l'évaluation | `evaluation_politique(pi, gamma)` |
| γ de bascule | `seuil_de_bascule()` |

Copiez le bloc dans `bellman_voyage.py` et lancez `python bellman_voyage.py`.

### Déroulé, ligne par ligne

Les états sont numérotés pour tenir dans une liste `V` : `0` recherche, `1` vol pas cher pris, `2` vol direct pris, `3` utilisateur content, `4` utilisateur épuisé. `TRANSITIONS` ne contient ni 3 ni 4 : ce sont des fins, il n'y a plus d'action et leur valeur vaut 0. Une transition est un triplet `(probabilité, récompense, état suivant)`. L'action « pas cher » depuis la recherche est `(1.00, 30.0, APRES_PAS_CHER)` : elle est sûre à 100 %, rapporte 30 tout de suite et mène à l'état 1.

**`backup_action(V, etat, action, gamma)`**. C'est Q(s, a), un terme de la somme de Bellman.

- `esperance = 0.0` : l'accumulateur de la somme sur s′.
- Pour chaque triplet : `contribution = proba * (recompense + gamma * V[suivant])`, puis `esperance += contribution`. La probabilité multiplie **toute** la parenthèse, récompense comprise.
- Exemple à γ = 0,10, une fois que `V[1]` vaut −20 : « pas cher » donne 1 × (30 + 0,10 × (−20)) = 28 ; « direct » donne 1 × (5 + 0,10 × 80) = 13.
- `return esperance` : ce n'est pas encore un choix, c'est la valeur d'une seule action.

**`T_etoile(V, gamma)`**. C'est l'opérateur 𝒯\* : une sauvegarde dans chaque état.

- `nouveau = [0.0] * len(V)` : on écrit dans une liste neuve, et les états finaux restent à 0. Si l'on écrivait dans `V` pendant le tour, l'état 0 lirait déjà la nouvelle valeur de l'état 1 : les valeurs intermédiaires et le nombre de tours dépendraient de l'ordre des états. Cette variante « en place » converge vers le même V\*, mais elle se raisonne moins bien.
- Pour chaque action, `candidat = backup_action(...)`, et l'on garde le plus grand avec `candidat > valeur`. En cas d'égalité exacte, la première action de la liste reste : à γ = 0,25, les deux valent 25 et « pas cher », écrite en premier, est gardée.
- La fonction renvoie `nouveau` et `politique`, l'action gloutonne de chaque état.

**`norme_inf(U, V)`** renvoie `max(abs(u - v) ...)` : le plus grand écart, pas la moyenne. C'est la norme que le théorème contrôle.

**`iteration_valeur(gamma)`** répète `T_etoile` depuis `V = [0.0] * 5`.

- Au tour 1, `V` est nulle : « pas cher » vaut 30 + 0 = 30 et « direct » vaut 5. L'hôtel après le vol pas cher vaut −20, l'hôtel après le vol direct 80.
- Au tour 2, ces valeurs futures existent. À γ = 0,10, « pas cher » tombe à 28 et « direct » monte à 13 : 28 gagne encore. À γ = 0,95, « pas cher » vaut 30 + 0,95 × (−20) = 11 et « direct » 5 + 0,95 × 80 = 81 : l'action optimale bascule.
- Au tour 3, les mêmes nombres reviennent, `ecart` vaut 0 et la fonction renvoie `(V, politique, 3)`.

**`evaluation_politique(pi, gamma)`** applique 200 fois l'opérateur d'évaluation : la même somme sur s′, mais pondérée par `pi[etat][a]` au lieu d'un maximum. Pour la politique à pile ou face, on obtient 0,5 × 11 + 0,5 × 81 = 46.

**`seuil_de_bascule()`** résout 30 − 20γ = 5 + 80γ et renvoie 25 / 100 = 0,25.

**`main()`**, bloc par bloc.

1. Pour γ = 0,10, 0,25 et 0,95, on lance l'itération de valeur et on imprime les deux Q. Les `assert` vérifient les nombres du tableau de la démonstration : 28, 13, 11, 81, l'égalité à 25, le seuil 0,25 et les 3 tours.
2. On évalue la politique à pile ou face : 46. On vérifie V^π ≤ V\* dans tous les états (point 5).
3. Le bloc « 20 % d'annulation » ne passe pas par l'itération : il calcule une seule sauvegarde, à deux branches. Branche 1 : 0,80 × (30 + 0,95 × (−20)) = 8,8. Branche 2 : 0,20 × (−50 + 0) = −10. Somme : −1,2.
4. On applique une sauvegarde à U = [0, 0, 0, 0, 0] et à W = [0, 10, 10, 0, 0] : l'écart passe de 10 à 9,5 = γ × 10 (point 3, borne atteinte).
5. L'état de veille rapporte +1 à chaque pas, pour toujours : V\* = 1 / (1 − 0,95) = 20, la borne du point 6. La boucle vérifie à chaque tour que l'erreur vaut exactement 20 × 0,95ᵏ (point 4). Elle s'arrête au tour 91, quand l'écart 0,95⁹⁰ ≈ 0,00989 passe sous 0,01. L'erreur vaut alors 0,1879, soit 19 fois l'écart : c'est exactement la borne γ / (1 − γ). Il faudrait 149 tours pour une erreur sous 0,01.
6. Les dernières lignes rappellent la propriété de Markov : si l'état oublie le budget restant, deux clients différents reçoivent la même valeur, donc la même action.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`backup_action(V, etat, action, gamma)`** — Cette fonction est l'agent de voyage qui, devant un comptoir, chiffre une seule option : elle reçoit le tableau V des valeurs actuelles, un état, une action et le facteur γ, parcourt les triplets (probabilité, récompense, état suivant) de cette action dans `TRANSITIONS`, et ajoute pour chacun la probabilité multipliée par la récompense augmentée de γ fois la valeur de l'état suivant. Elle renvoie cette espérance, la valeur Q(s, a) d'une action et non encore un choix ; à γ = 0,10, « pas cher » vaut 28 et « direct » 13, tandis qu'à γ = 0,95 « pas cher » tombe à 11 et « direct » monte à 81.

**`T_etoile(V, gamma)`** — C'est le directeur d'agence qui fait le tour de tous les comptoirs et retient, à chacun, la meilleure offre : la fonction reçoit le tableau V et γ, prépare une liste neuve remplie de zéros, pour que les états finaux restent à 0 et que l'ordre de parcours ne change rien, puis, pour chaque état non final, calcule par `backup_action` la valeur de chaque action et garde la plus grande, la première en cas d'égalité exacte. Elle renvoie le nouveau tableau des valeurs, l'application de l'opérateur 𝒯\*, ainsi que la politique gloutonne, l'action retenue dans chaque état ; à γ = 0,25, les deux actions valent 25 et c'est « pas cher », écrite en premier, qui reste.

**`norme_inf(U, V)`** — Cette petite fonction est l'arpenteur qui ne s'intéresse qu'au plus grand écart entre deux cartes : elle reçoit deux tableaux de valeurs U et V, calcule la valeur absolue de la différence état par état et renvoie la plus grande, la norme infinie ‖U − V‖∞, et non une moyenne. C'est la norme que contrôle le théorème de contraction : `iteration_valeur` s'en sert comme critère d'arrêt, et `main` montre au bloc 4 qu'un écart de 10 entre U et W devient exactement 9,5, soit γ × 10, après une application de 𝒯\*.

**`iteration_valeur(gamma, tol, max_tours)`** — On peut la voir comme un cartographe qui redessine sa carte des valeurs jusqu'à ce qu'elle cesse de bouger : la fonction reçoit γ, une tolérance de 10⁻¹⁰ par défaut et un nombre maximal de 1 000 tours, part d'un tableau de cinq zéros et applique `T_etoile` encore et encore, en mesurant à chaque tour le plus grand écart avec la carte précédente. Dès que cet écart passe sous la tolérance, elle renvoie la valeur V\*, la politique optimale et le nombre de tours, 3 ici, deux pour propager les récompenses et un pour constater qu'elles ne changent plus ; si la convergence n'arrive jamais, elle lève une `RuntimeError`.

**`evaluation_politique(pi, gamma, tours)`** — Cette fonction joue l'auditeur qui ne cherche pas la meilleure stratégie mais mesure ce que rapporte une stratégie donnée : elle reçoit une politique π, qui donne pour chaque état la probabilité de chaque action, le facteur γ et un nombre de tours, 200 par défaut, puis répète l'opérateur d'évaluation, où la valeur d'un état est la moyenne des valeurs des actions pondérée par π au lieu de leur maximum. Elle renvoie le tableau V^π ; pour la politique à pile ou face à γ = 0,95, la recherche vaut 0,5 × 11 + 0,5 × 81 = 46, et `main` vérifie que cette valeur ne dépasse V\* dans aucun état.

**`seuil_de_bascule()`** — Cette fonction est le calcul de coin de table qui dit à partir de quelle patience l'agent change d'avis : elle ne reçoit rien et résout l'égalité entre la valeur du vol pas cher, 30 − 20γ, et celle du vol direct, 5 + 80γ, ce qui donne γ = 25 / 100. Elle renvoie 0,25, la valeur où les deux actions se valent exactement ; `main` l'affiche en tête du bloc 1 et vérifie par un `assert` qu'elle vaut bien 0,25, en accord avec l'égalité à 25 obtenue par l'itération de valeur.

**`main()`** — Le chef d'orchestre joue les six tableaux du chapitre sur l'agent de réservation : il lance l'itération de valeur pour γ = 0,10, 0,25 et 0,95, imprime les deux valeurs Q et vérifie 28, 13, 11, 81, l'égalité à 25 et les 3 tours, puis évalue la politique à pile ou face, 46, et calcule à la main une sauvegarde à deux branches avec 20 % d'annulation, qui donne −1,2. Il montre ensuite la contraction, de 10 à 9,5, puis fait tourner un état de veille qui rapporte +1 pour toujours, s'arrête au tour 91 avec une erreur de 0,1879 et annonce qu'il en faudrait 149 pour une erreur sous 0,01 ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 38 — MDP et équation de Bellman sur l'agent de réservation. Bibliothèque standard."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# États de l'agent de voyage.
RECHERCHE, APRES_PAS_CHER, APRES_DIRECT, CONTENT, MECONTENT = range(5)
NOMS = {
    RECHERCHE: "recherche",
    APRES_PAS_CHER: "vol pas cher pris",
    APRES_DIRECT: "vol direct pris",
    CONTENT: "utilisateur content",
    MECONTENT: "utilisateur épuisé",
}
TERMINAUX = {CONTENT, MECONTENT}

# transitions[etat][action] = liste de (probabilité, récompense, état suivant)
# Version déterministe du cas du cours : chaque action a une seule suite.
# Le vol pas cher paie tout de suite (+30) et mène à l'épuisement (−20).
# Le vol direct paie peu (+5) et mène à l'utilisateur content (+80).
TRANSITIONS = {
    RECHERCHE: {
        "pas_cher": [(1.00, 30.0, APRES_PAS_CHER)],
        "direct": [(1.00, 5.0, APRES_DIRECT)],
    },
    APRES_PAS_CHER: {
        "hotel": [(1.00, -20.0, MECONTENT)],
    },
    APRES_DIRECT: {
        "hotel": [(1.00, 80.0, CONTENT)],
    },
}


def backup_action(V: list[float], etat: int, action: str, gamma: float) -> float:
    """Q(s, a) = Σ_{s'} P(s'|s,a) [ R + γ V(s') ]."""
    esperance = 0.0
    for proba, recompense, suivant in TRANSITIONS[etat][action]:
        contribution = proba * (recompense + gamma * V[suivant])
        esperance += contribution
    return esperance


def T_etoile(V: list[float], gamma: float) -> tuple[list[float], dict[int, str]]:
    """(T* V)(s) = max_a Q(s, a) ; un état terminal vaut 0. Renvoie aussi l'action gloutonne."""
    nouveau = [0.0] * len(V)                 # les terminaux restent à 0 : il n'y a plus rien à gagner
    politique = {}
    for etat, actions in TRANSITIONS.items():
        valeur, choix = None, None
        for action in actions:               # en cas d'égalité parfaite, la première action reste
            candidat = backup_action(V, etat, action, gamma)
            if valeur is None or candidat > valeur:
                valeur, choix = candidat, action
        nouveau[etat] = valeur
        politique[etat] = choix
    return nouveau, politique


def norme_inf(U: list[float], V: list[float]) -> float:
    return max(abs(u - v) for u, v in zip(U, V))


def iteration_valeur(gamma: float, tol: float = 1e-10, max_tours: int = 1000):
    """V_{k+1} = T* V_k depuis V_0 = 0, jusqu'à ce que le plus grand écart passe sous tol."""
    V = [0.0] * 5
    for tour in range(1, max_tours + 1):
        nouveau, politique = T_etoile(V, gamma)
        ecart = norme_inf(nouveau, V)
        V = nouveau
        if ecart < tol:
            return V, politique, tour
    raise RuntimeError("la valeur n'a pas convergé")


def evaluation_politique(pi: dict[int, dict[str, float]], gamma: float, tours: int = 200) -> list[float]:
    """V^π(s) = Σ_a π(a|s) Σ_{s'} P [ R + γ V^π(s') ] : une moyenne pondérée, pas un max."""
    V = [0.0] * 5
    for _ in range(tours):
        nouveau = [0.0] * 5
        for etat, actions in TRANSITIONS.items():
            nouveau[etat] = sum(pi[etat][a] * backup_action(V, etat, a, gamma) for a in actions)
        V = nouveau
    return V


def seuil_de_bascule() -> float:
    """γ à partir duquel le vol direct bat le vol pas cher : 30 − 20γ = 5 + 80γ ⇒ γ = 25/100."""
    return (30.0 - 5.0) / (80.0 + 20.0)


def main() -> None:
    print("=== 1. Le γ fait changer d'action (itération de valeur : on calcule V*) ===")
    print(f"  les deux actions se valent à γ = {seuil_de_bascule():.2f}")
    print(f"  {'γ':>6}  {'action choisie':<16}  {'V*(recherche)':>14}  tours")
    resultats = {}
    for gamma in (0.10, 0.25, 0.95):
        V, politique, tours = iteration_valeur(gamma)
        resultats[gamma] = (V, politique, tours)
        print(f"  {gamma:6.2f}  {politique[RECHERCHE]:<16}  {V[RECHERCHE]:14.4f}  {tours}")
        for action in ("pas_cher", "direct"):
            etiquette = "Q(" + action + ")"
            print(f"      {etiquette:<12} = {backup_action(V, RECHERCHE, action, gamma):8.3f}")
    V, politique, _ = resultats[0.95]
    print("    détail des états à γ = 0.95 :")
    for etat in range(5):
        print(f"      {NOMS[etat]:22s}  V* = {V[etat]:8.3f}   action = {politique.get(etat, '—')}")

    # Les nombres calculés à la main dans la démonstration.
    V10, pi10, _ = resultats[0.10]
    V25, pi25, _ = resultats[0.25]
    V95, pi95, tours95 = resultats[0.95]
    assert abs(backup_action(V10, RECHERCHE, "pas_cher", 0.10) - 28.0) < 1e-9
    assert abs(backup_action(V10, RECHERCHE, "direct", 0.10) - 13.0) < 1e-9
    assert abs(backup_action(V95, RECHERCHE, "direct", 0.95) - 81.0) < 1e-9
    assert abs(backup_action(V95, RECHERCHE, "pas_cher", 0.95) - 11.0) < 1e-9
    assert pi10[RECHERCHE] == "pas_cher" and pi95[RECHERCHE] == "direct"
    assert seuil_de_bascule() == 0.25
    assert V25[RECHERCHE] == 25.0 and pi25[RECHERCHE] == "pas_cher"   # égalité : la première action reste
    assert tours95 == 3                     # profondeur 2 : deux tours pour propager, un pour constater

    print("\n=== 2. Évaluer une politique (V^π) n'est pas optimiser (V*) ===")
    pi_hasard = {RECHERCHE: {"pas_cher": 0.5, "direct": 0.5},
                 APRES_PAS_CHER: {"hotel": 1.0}, APRES_DIRECT: {"hotel": 1.0}}
    V_pi = evaluation_politique(pi_hasard, 0.95)
    print(f"  π = 50 % / 50 % à γ = 0.95 : V^π(recherche) = 0.5 × 11 + 0.5 × 81 = {V_pi[RECHERCHE]:.3f}")
    print(f"  V*(recherche) = {V95[RECHERCHE]:.3f} : aucune politique ne fait mieux")
    assert abs(V_pi[RECHERCHE] - 46.0) < 1e-9
    assert all(V_pi[s] <= V95[s] + 1e-9 for s in range(5))

    print("\n=== 3. Pourquoi l'espérance, et pas une seule récompense ===")
    # Ici le vol pas cher peut être annulé. Ce n'est plus le MDP optimisé au-dessus :
    # on calcule UNE sauvegarde de Bellman, à la main, pour voir la somme pondérée.
    V_apres = {APRES_PAS_CHER: -20.0, MECONTENT: 0.0}
    gamma = 0.95
    branches = [
        (0.80, 30.0, APRES_PAS_CHER),
        (0.20, -50.0, MECONTENT),
    ]
    print("  action « pas cher » avec 20 % d'annulation, γ = 0.95 :")
    total = 0.0
    for proba, recompense, suivant in branches:
        terme = proba * (recompense + gamma * V_apres[suivant])
        total += terme
        print(f"    {proba:.0%}  R = {recompense:6.1f}  état suivant = {NOMS[suivant]:20s}  contribution = {terme:7.3f}")
    print(f"    somme = {total:.3f}")
    assert abs(total - (-1.2)) < 1e-9

    print("\n=== 4. Contraction : ||T*U − T*W||∞ ≤ γ ||U − W||∞ ===")
    U = [0.0, 0.0, 0.0, 0.0, 0.0]
    W = [0.0, 10.0, 10.0, 0.0, 0.0]
    avant = norme_inf(U, W)
    apres = norme_inf(T_etoile(U, 0.95)[0], T_etoile(W, 0.95)[0])
    print(f"  ||U − W||∞ = {avant:.2f} ; ||T*U − T*W||∞ = {apres:.2f} ; γ × {avant:.0f} = {0.95 * avant:.2f}")
    assert apres <= 0.95 * avant + 1e-12 and abs(apres - 9.5) < 1e-9   # ici la borne est atteinte

    print("\n=== 5. Un état qui boucle : borne R_max/(1 − γ), vitesse γ^k, critère d'arrêt ===")
    # Agent de veille : +1 à chaque pas, pour toujours. V* = 1/(1 − γ) = 20 à γ = 0.95.
    g = 0.95
    v_etoile = 1.0 / (1.0 - g)
    v, k = 0.0, 0
    while True:
        k += 1
        v_suivant = 1.0 + g * v               # T* sur un seul état, une seule action
        ecart = abs(v_suivant - v)
        v = v_suivant
        if k in (1, 10, 50):
            print(f"  tour {k:3d}  V = {v:8.4f}  erreur = {v_etoile - v:7.4f}  20 × 0.95^{k} = {20 * g ** k:7.4f}")
        assert abs((v_etoile - v) - v_etoile * g ** k) < 1e-9     # erreur exacte : γ^k ||V0 − V*||
        if ecart < 0.01:
            break
    erreur = v_etoile - v
    print(f"  arrêt au tour {k} : écart {ecart:.5f} < 0.01, mais erreur {erreur:.4f} = 19 × écart")
    assert k == 91 and abs(erreur - g / (1 - g) * ecart) < 1e-9
    k_min = math.ceil(math.log(0.01 / v_etoile) / math.log(g))
    print(f"  pour une erreur < 0.01, il faut k ≥ ln(0.01/20) / ln 0.95 = {k_min} tours")
    assert k_min == 149
    print(f"  horizon effectif 1/(1 − γ) = {v_etoile:.0f} pas ; poids d'une récompense à 20 pas : 0.95^20 = {g ** 20:.4f}")
    assert g ** 20 <= math.exp(-1)

    print("\n=== 6. Propriété de Markov : l'état doit contenir ce qui compte ===")
    print("  Si l'état « recherche » oublie le budget restant, deux clients différents")
    print("  ont le même V, donc la même action : la planification se trompe.")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. Le γ fait changer d'action (itération de valeur : on calcule V*) ===
  les deux actions se valent à γ = 0.25
    0.10  pas_cher                 28.0000  3
      Q(pas_cher)  =   28.000
      Q(direct)    =   13.000
    0.25  pas_cher                 25.0000  3
    0.95  direct                   81.0000  3
      Q(pas_cher)  =   11.000
      Q(direct)    =   81.000
…
  π = 50 % / 50 % à γ = 0.95 : V^π(recherche) = 0.5 × 11 + 0.5 × 81 = 46.000
…
    somme = -1.200
…
  ||U − W||∞ = 10.00 ; ||T*U − T*W||∞ = 9.50 ; γ × 10 = 9.50
…
  arrêt au tour 91 : écart 0.00989 < 0.01, mais erreur 0.1879 = 19 × écart
  pour une erreur < 0.01, il faut k ≥ ln(0.01/20) / ln 0.95 = 149 tours
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : γ n'est pas un réglage cosmétique du prompt « pense à long terme ». Dans ce MDP, il change l'action optimale. La contraction garantit que l'itération trouve la bonne valeur depuis n'importe quel départ, et le critère d'arrêt se lit avec son facteur γ / (1 − γ). Enfin, l'état doit contenir le budget, sinon deux situations différentes reçoivent la même valeur.

## Squelette algorithmique

Le fichier contient deux algorithmes. L'**itération de valeur** prend en entrée un MDP fini (les états, les actions possibles dans chaque état, et pour chaque couple état-action la liste des triplets probabilité, récompense, état suivant), un facteur γ et un seuil ε. Elle renvoie une estimation de V\*, la politique gloutonne qui en découle et le nombre de tours effectués. L'idée est d'appliquer l'opérateur 𝒯\* encore et encore, en partant de V = 0 : la contraction (point 3) garantit que les estimations se rapprochent de V\* d'un facteur γ à chaque tour, et l'on s'arrête quand deux tours successifs ne diffèrent presque plus, en sachant que l'erreur restante vaut au plus γ ε / (1 − γ) (point 4). L'**évaluation d'une politique** prend en entrée la même description du MDP, une politique stochastique π et un nombre de tours ; elle renvoie V^π en appliquant l'opérateur d'évaluation, qui fait une moyenne pondérée par π là où l'itération de valeur prend un maximum.

```text
ALGORITHME IterationDeValeur
ENTRÉES : états S, actions A(s), transitions P(s, a) = liste de (p, r, s′), facteur γ, seuil ε
SORTIE : valeurs V, politique π, nombre de tours k

V(s) ← 0 pour chaque état s
k ← 0
TANT QUE vrai FAIRE
    k ← k + 1
    POUR chaque état s FAIRE
        SI s est terminal ALORS
            V′(s) ← 0
        SINON
            meilleure ← −∞
            POUR chaque action a de A(s) FAIRE
                q ← Σ sur les (p, r, s′) de P(s, a) de p × (r + γ × V(s′))
                SI q > meilleure ALORS
                    meilleure ← q
                    π(s) ← a
                FIN SI
            FIN POUR
            V′(s) ← meilleure
        FIN SI
    FIN POUR
    écart ← max sur s de |V′(s) − V(s)|
    V ← V′
    SI écart < ε ALORS
        RETOURNER V, π, k          (erreur garantie ≤ γ × écart / (1 − γ))
    FIN SI
FIN TANT QUE
```

```text
ALGORITHME EvaluationDePolitique
ENTRÉES : états S, transitions P(s, a), politique π(a | s), facteur γ, nombre de tours N
SORTIE : valeurs V^π

V(s) ← 0 pour chaque état s
POUR t DE 1 À N FAIRE
    POUR chaque état s FAIRE
        SI s est terminal ALORS
            V′(s) ← 0
        SINON
            V′(s) ← Σ sur a de π(a | s) × Σ sur les (p, r, s′) de P(s, a) de p × (r + γ × V(s′))
        FIN SI
    FIN POUR
    V ← V′
FIN POUR
RETOURNER V
```

**Complexité :** on note |S| le nombre d'états, |A| le nombre maximal d'actions par état et b le nombre maximal d'états suivants d'un couple état-action. Un tour lit chaque triplet une fois et fait, pour chacun, une multiplication et une addition : il coûte O(|S| × |A| × b) opérations, soit O(|S|² × |A|) dans le pire cas où chaque action peut mener partout. Le calcul de l'écart ajoute O(|S|). Le nombre de tours vient de la contraction : pour garantir ‖Vₖ − V\*‖∞ ≤ δ, il suffit que γᵏ ‖V₀ − V\*‖∞ ≤ δ, c'est-à-dire k ≥ ln(‖V₀ − V\*‖∞ / δ) / ln(1/γ) ; comme ln(1/γ) ≥ 1 − γ, il suffit de O(ln(‖V₀ − V\*‖∞ / δ) / (1 − γ)) tours, ce qui donne les 149 tours de l'exemple de la veille. Dans un MDP sans cycle, le nombre de tours tombe à la profondeur du graphe plus un. La mémoire vaut O(|S|) pour les deux listes V et V′ et pour π, plus O(|S| × |A| × b) pour la table des transitions elle-même. L'évaluation d'une politique a le même coût par tour, multiplié par N tours.

**Du squelette au code :** l'initialisation « V(s) ← 0 » et la boucle « TANT QUE » sont dans `iteration_valeur`, qui remplace le « TANT QUE vrai » par `for tour in range(1, max_tours + 1)` et lève une `RuntimeError` si la valeur ne converge pas : c'est un garde-fou que le pseudo-code omet. Le corps « POUR chaque état s » est la fonction `T_etoile`, où « V′(s) ← 0 » pour les terminaux vient de `nouveau = [0.0] * len(V)` et où « SI q > meilleure » s'écrit `if valeur is None or candidat > valeur`. La ligne « q ← Σ … » est exactement `backup_action(V, etat, action, gamma)`. La ligne « écart ← max … » est `norme_inf(nouveau, V)`, et le test « SI écart < ε » est `if ecart < tol`. L'algorithme d'évaluation correspond ligne pour ligne à `evaluation_politique`, avec `tours = 200` pour N et `pi[etat][a] * backup_action(...)` pour la somme pondérée.

## Cas d'usage réels aux Émirats

Les probabilités, récompenses et facteurs γ ci-dessous sont illustratifs. En production, on les estime sur l'historique de chaque métier, et l'équipe métier valide le barème des récompenses, parce que l'agent optimisera exactement ce qui est écrit.

### Secteur public — clarifier avant de répondre

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais aux questions sur le renouvellement des documents. Quand une demande est ambiguë (« je veux renouveler ma carte », sans dire laquelle), l'agent peut répondre tout de suite ou poser une question de clarification. L'équipe modélise ce choix comme un petit MDP : une bonne réponse vaut +10, une mauvaise −20 (l'usager mal orienté rappelle, se plaint ou abandonne), et une question coûte −1, le prix d'un tour de plus. Sur une demande ambiguë, une réponse immédiate est juste 60 % du temps, contre 95 % après clarification. Répondre tout de suite vaut 0,6 × 10 + 0,4 × (−20) = −2 ; clarifier vaut −1 + 0,9 × (0,95 × 10 + 0,05 × (−20)) = −1 + 0,9 × 8,5 = 6,65, avec γ = 0,9 par tour. L'agent clarifie donc, mais seulement quand son classifieur a jugé la demande ambiguë : sur une demande claire, la question coûterait un tour pour rien. Pour respecter la minimisation des données de la PDPL, la question porte sur le type de document, jamais sur une donnée personnelle qui ne sert pas à la réponse. On suit le taux de résolution au premier contact et le nombre moyen de tours par demande.

### Banque — rééchelonner ou relancer un prêt en retard

Une banque de détail de Dubaï confie à un agent la préparation des actions de recouvrement amiable sur les prêts personnels en retard de 30 jours. La relance standard ne coûte rien, mais elle ne régularise qu'un dossier sur deux (valeur +100) ; l'autre moitié passe en retard de 60 jours, un état dont la valeur estimée vaut −200 (provisions, coût de recouvrement). Le rééchelonnement coûte 30 (intérêts abandonnés) mais régularise 85 % des dossiers. Avec γ = 0,9 par mois, la relance vaut 0,5 × 100 + 0,5 × (0 + 0,9 × (−200)) = −40, et le rééchelonnement 0,85 × (100 − 30) + 0,15 × (−30 + 0,9 × (−200)) = 59,5 − 31,5 = 28. L'agent propose donc le rééchelonnement, qu'un conseiller valide. Une règle qui choisirait l'action la moins chère aujourd'hui, la relance à coût nul, ignorerait la valeur −200 de l'état suivant. Le nouvel échéancier doit respecter la règle de la CBUAE : toutes les mensualités du client, y compris la nouvelle, restent sous 50 % de son revenu ; l'agent appelle l'outil `ratio_endettement` avant de proposer. On suit le taux de régularisation à 90 jours et le taux de passage en retard de 60 jours.

### Immobilier — valoriser un pipeline de commissions sur plan

Une agence de Dubaï et d'Abu Dhabi utilise un agent pour prévoir son pipeline de commissions et répartir le temps de ses négociateurs seniors. Une vente de bien prêt à livrer rapporte, dans cet exemple, 20 000 AED tout de suite ; une vente sur plan rapporte 30 000 AED en trois tranches de 10 000 AED, aux semaines 0, 26 et 52. C'est le retour Gₜ du point 1, avec des récompenses nulles entre les tranches : avec γ = 0,98 par semaine (horizon effectif de 50 semaines), la vente sur plan vaut 10 000 × (1 + 0,98²⁶ + 0,98⁵²) = 10 000 × (1 + 0,5914 + 0,3497) ≈ 19 411 AED, moins que les 20 000 AED du bien prêt. Avec γ = 0,99 (horizon de 100 semaines), elle vaut 10 000 × (1 + 0,7700 + 0,5930) ≈ 23 630 AED et passe devant. La décision bascule avec γ : il doit donc venir d'un choix écrit et validé par la direction financière (coût du capital, risque qu'une tranche ne soit jamais versée), pas d'une valeur par défaut. Sans actualisation, l'agent compterait 30 000 AED et surpondérerait les dossiers longs. Les fonds des acheteurs sur plan passent par des comptes séquestres et les ventes sont enregistrées auprès du DLD : le versement de chaque tranche dépend de l'avancement du projet et du contrat, à confirmer avec les règles en vigueur. L'agent priorise le travail de l'agence, il n'oriente jamais le choix de l'acheteur. On suit l'écart entre la valeur prévue du pipeline et les commissions réellement encaissées, trimestre par trimestre.

### Crypto — escalader une alerte de liquidité ou attendre une heure

Une plateforme d'actifs virtuels agréée par la VARA fait surveiller par un agent la liquidité de ses portefeuilles chauds. Quand une alerte se déclenche, l'agent peut escalader tout de suite à l'astreinte, ce qui coûte −2 (un opérateur réveillé, une procédure manuelle), ou attendre une heure. Si l'on attend, la situation tourne à la crise dans 20 % des cas (valeur −50 : des retraits bloqués) et se résorbe seule dans 80 % des cas (valeur 0). Attendre vaut 0,2 × (0 + γ × (−50)) = −10γ, escalader vaut −2 : il faut escalader dès que 10γ > 2, c'est-à-dire γ > 0,2. Avec γ = 0,9 par heure, attendre vaut −9 et l'agent escalade ; un agent myope réglé à γ = 0,1 verrait −1 contre −2 et attendrait, et il aurait tort une fois sur cinq, au pire moment. La valeur −50 n'est pas une perte mesurée : c'est un poids de gravité que l'équipe des risques fixe et révise. La VARA attend une gestion documentée du risque de liquidité et de la protection des avoirs des clients (à confirmer avec le règlement en vigueur) : chaque décision, escalade ou attente, est journalisée avec ses deux valeurs Q. On suit le délai entre la première alerte et la prise en charge, et le nombre d'incidents de retrait bloqué.

### Assurance — demander une expertise ou indemniser directement

Un assureur auto et santé confie à un agent le tri des petits sinistres automobiles. Indemniser directement coûte le montant A réclamé. Demander une expertise coûte 300 AED, puis 10 % des dossiers se révèlent injustifiés (on paie 0) et 90 % sont payés au montant A. L'épisode a deux pas et se termine toujours : on peut prendre γ = 1 (point 1). Indemniser vaut −A ; l'expertise vaut −300 − 0,9 A ; elle est meilleure dès que 0,1 A > 300, c'est-à-dire pour A > 3 000 AED. Pour un sinistre de 4 000 AED, −3 900 bat −4 000 et l'agent demande l'expertise ; pour 1 500 AED, −1 500 bat −1 650 et il indemnise. Ce cas montre aussi un piège : avec des coûts et γ < 1, payer plus tard paraît moins cher, et un agent serait tenté de retarder les paiements. On garde donc γ = 1 sur ce sous-problème court, ou l'on ajoute une pénalité par jour d'attente. L'assurance est supervisée par la CBUAE, qui attend un traitement équitable et diligent des sinistres : l'agent ne refuse jamais un dossier seul, il demande une expertise, et la décision reste humaine. On suit le coût moyen par sinistre (indemnité et expertise comprises), le délai moyen de règlement et la part des expertises qui changent le montant.

### RH — choisir γ selon la longueur d'un dossier d'intégration

Un cabinet RH présent dans plusieurs émirats fait ordonner par un agent les tâches d'intégration d'un salarié venu de l'étranger : visite médicale, visa, Emirates ID, contrat auprès du MOHRE, compte de paie compatible WPS. La récompense +100 arrive quand le salarié est opérationnel et reçoit son premier salaire via le WPS. L'option A lance d'abord le chemin critique (la visite médicale) : la récompense arrive dans 10 pas et vaut 100 γ¹⁰. L'option B traite d'abord les tâches faciles (le kit de bienvenue rapporte +5 tout de suite) et repousse la récompense finale à 13 pas : 5 + 100 γ¹³. Avec γ = 0,5, dont l'horizon effectif est de 2 pas, A vaut 0,098 et B vaut 5,01 : l'agent « a l'air occupé » mais retarde la prise de poste de trois pas. Avec γ = 0,95, dont l'horizon de 20 pas couvre la durée du processus, A vaut 59,87 et B vaut 5 + 51,33 = 56,33 : l'agent lance le chemin critique. La règle pratique est de choisir γ pour que 1 / (1 − γ) couvre la longueur du processus. Les démarches auprès du MOHRE et le paiement par le WPS ont des dépendances strictes (étape 37 bis) que l'état doit contenir. On suit le délai moyen entre la signature du contrat et le premier salaire versé.

## Pièges et limites

- **Une récompense mal écrite est optimisée quand même.** L'agent maximise ce qui est écrit, pas ce que l'on voulait : si la récompense vient d'un juge LLM, l'agent apprend à plaire au juge (reward hacking). Le barème se relit et se teste comme du code.
- **Un état qui n'est pas markovien.** Si l'état oublie une information qui change la suite (le budget restant, le nombre de relances déjà faites), deux situations différentes reçoivent la même valeur et la même action.
- **γ = 1 sur une tâche qui peut boucler.** La contraction disparaît et les valeurs peuvent diverger. γ = 1 n'est sûr que si chaque épisode se termine, comme dans l'exemple du vol ou de l'assurance.
- **Confondre l'écart entre deux tours et l'erreur.** Un écart ε garantit seulement une erreur inférieure à γ ε / (1 − γ) : 19 ε à γ = 0,95.
- **Des probabilités fragiles et des états trop nombreux.** Une probabilité estimée sur vingt dossiers peut changer la décision : on vérifie que l'action choisie résiste à une variation de ±0,1. Un MDP tabulaire demande d'énumérer tous les états : dès que l'état contient du texte libre ou des dizaines de variables, c'est impossible. On approche alors V (MCTS, évaluateur LLM), et l'on perd les garanties démontrées ici.

### Exercice feuille blanche

1. Sans regarder le code, écrire `backup_action` et `T_etoile` à partir de l'équation d'optimalité, puis vérifier 28 et 13 à γ = 0,10.
2. Prédire, puis vérifier : à γ = 0,5, quelle action est choisie et que vaut V\*(recherche) ? (Réponse : 30 − 10 = 20 contre 5 + 40 = 45 : vol direct, V\* = 45.) Pour l'état de veille à γ = 0,9, à quel tour l'écart passe-t-il sous 0,01, et que vaut alors l'erreur ? (Réponse : au tour 45, quand 0,9⁴⁴ ≈ 0,0097 ; l'erreur vaut 9 fois l'écart, environ 0,087.)
3. Trouver le bug : `contribution = proba * recompense + gamma * V[suivant]`. Que donne l'exemple de l'annulation à 20 % ? (Réponse : 0,8 × 30 + 0,95 × (−20) + 0,2 × (−50) + 0 = −5 au lieu de −1,2 : la valeur future n'est plus pondérée par la probabilité de sa branche.)

## Pour aller plus loin

- **Itération de politique** : évaluer π (comme `evaluation_politique`), la rendre gloutonne, recommencer. Dans un MDP fini, elle s'arrête après un nombre fini d'améliorations.
- **Q-learning** : quand 𝒫 est inconnue, on apprend Q à partir d'échantillons de transitions, sans écrire le modèle.
- **MCTS et Tree of Thoughts** : on n'explore qu'une partie de l'arbre, et un évaluateur estime la valeur des feuilles.
- La seconde moitié des fondements (étape 39) rejoue la contraction sur un MDP à deux états qui boucle, avec des nombres différents.

> Suite : [Bellman et contraction, seconde moitié des fondements](<../02-LLM-Softmax-et-Prompts/03-Fondements-Softmax-et-LLM.md>) — étape 39 : relire la partie « 3. Processus de Décision Markovien (MDP) et Équation de Bellman ».
