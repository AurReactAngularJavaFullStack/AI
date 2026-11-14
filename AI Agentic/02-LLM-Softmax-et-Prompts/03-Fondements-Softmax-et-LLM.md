# Étape 3 — La Fonction Softmax, Température et Échantillonnage Probabiliste des LLM

> Étapes 3 et 39 du parcours · Prérequis : [Tokenisation BPE](<02b-Tokenisation-BPE.md>) pour l'étape 3, [MDP et planification](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>) pour l'étape 39 · Suite : [Prompts : définitions fondamentales](<04-Prompts-Definitions-Fondamentaux.md>) après l'étape 3, [Coût A\*](<../07-Planification/40-Planification-Formule-A-Star.md>) après l'étape 39

Ce fichier se lit en deux fois. À l'étape 3, on lit la première moitié (softmax, jacobien, gradient, température), qui reprend et prolonge le chapitre de l'étape 2. À l'étape 39, juste après le chapitre sur les MDP, on relit la seconde moitié (équation de Bellman et contraction).

## 1. Contextualisation et Rôle dans le Développement d'Agents IA

Au cœur de tout modèle de langage (LLM) sous-jacent à un agent autonome (modèle propriétaire appelé par API, ou modèle ouvert comme Jais ou Falcon), la dernière couche du réseau de neurones produit des scores bruts non normalisés appelés **logits**

$$
z \in \mathbb{R}^{|V|} ,
$$

où |V| représente la taille du vocabulaire (ex: |V| ≈ 100 000 tokens).

Pour qu'un agent prenne une décision (sélectionner un outil, générer du code, répondre à une requête), ces logits doivent être transformés en une **distribution de probabilité catégorielle** valide

$$
P \in \Delta^{|V|-1}
$$

sur l'ensemble du vocabulaire.

Un **AI Agentic Developer** doit maîtriser les propriétés analytiques de la fonction Softmax pour :
* Contrôler le niveau de créativité vs déterminisme de l'agent via le paramètre de **Température** T.
* Comprendre le phénomène de **saturation des gradients** lors du Fine-Tuning / RLHF (Reinforcement Learning from Human Feedback).
* Implémenter des algorithmes de décodage avancés (Top-k, Top-p / Nucleus Sampling, Min-P) pour couper les tokens aberrants et limiter les répétitions (ces techniques réduisent certains défauts du tirage ; elles n'empêchent pas un modèle d'halluciner).

---

## 2. Définition Mathématique Formelle

Soit

$$
z = (z_1, z_2, \dots, z_{|V|})^T \in \mathbb{R}^{|V|}
$$

le vecteur des logits sortant du Transformer.

### A. La Fonction Softmax Standard

La fonction **Softmax** est l'application

$$
\sigma : \mathbb{R}^{|V|} \to ]0, 1[^{|V|}
$$

définie pour chaque composante i ∈ {1, …, |V|} par :

$$
p_i = \sigma(z)_i = \frac{e^{z_i}}{\sum_{j=1}^{|V|} e^{z_j}}
$$

### B. Propriétés Fondamentales

1. **Strictement Positif** : ∀ i ∈ {1, …, |V|}, pᵢ > 0.
2. **Conservation de la Masse (Normalisation)** : 

$$
\sum_{i=1}^{|V|} p_i = \frac{\sum_{i=1}^{|V|} e^{z_i}}{\sum_{j=1}^{|V|} e^{z_j}} = 1
$$

3. **Invariance par translation** (l'ancien titre disait « fréquentielle », ce qui n'a pas de sens ici : on ajoute la même constante à tous les logits). Pour tout scalaire c ∈ ℝ :

$$
\sigma(z + c \mathbf{1})_i = \frac{e^{z_i + c}}{\sum_{j=1}^{|V|} e^{z_j + c}} = \frac{e^c \cdot e^{z_i}}{e^c \sum_{j=1}^{|V|} e^{z_j}} = \sigma(z)_i
$$

   *(Cette propriété est exploitée informatiquement pour assurer la stabilité numérique en choisissant c = −maxⱼ(zⱼ) pour éviter le sous-flux ou sur-flux flottant).*

---

## 3. Démonstration Mathématique : Gradient de la Softmax et Perte Cross-Entropy

Lors de l'entraînement ou de l'alignement DPO/PPO d'un agent IA, l'optimisation des poids repose sur le calcul de la dérivée partielle de la fonction Softmax par rapport aux logits bruts.

### Théorème (Matrice Jacobienne de la Softmax) :

La dérivée partielle de la probabilité pᵢ par rapport au logit zₖ est donnée par :

$$
\frac{\partial p_i}{\partial z_k} = \begin{cases} p_i (1 - p_i) & \text{si } i = k \\ -p_i p_k & \text{si } i \neq k \end{cases}
$$

Ce que l'on résume avec le symbole de Kronecker δᵢₖ par :

$$
\frac{\partial p_i}{\partial z_k} = p_i (\delta_{ik} - p_k)
$$

### Démonstration Étape par Étape :

Soit

$$
p_i = \frac{u_i}{v}
$$

avec

$$
u_i = e^{z_i}
$$

et

$$
v = \sum_{j=1}^{|V|} e^{z_j} .
$$

Appliquons la règle de dérivation d'un quotient

$$
\left( \frac{u}{v} \right)' = \frac{u'v - uv'}{v^2}
$$

1. **Cas 1 : i = k**

$$
\frac{\partial u_i}{\partial z_i} = \frac{\partial (e^{z_i})}{\partial z_i} = e^{z_i}
$$

$$
\frac{\partial v}{\partial z_i} = \frac{\partial (\sum_j e^{z_j})}{\partial z_i} = e^{z_i}
$$

   * Calcul de la dérivée :

$$
\frac{\partial p_i}{\partial z_i} = \frac{e^{z_i} \cdot v - e^{z_i} \cdot e^{z_i}}{v^2} = \frac{e^{z_i}}{v} \left( \frac{v - e^{z_i}}{v} \right) = p_i \left( 1 - \frac{e^{z_i}}{v} \right) = p_i (1 - p_i)
$$

2. **Cas 2 : i ≠ k**

$$
\frac{\partial u_i}{\partial z_k} = 0
$$

(car

$$
u_i = e^{z_i}
$$

ne dépend pas de zₖ)

$$
\frac{\partial v}{\partial z_k} = e^{z_k}
$$

   * Calcul de la dérivée :

$$
\frac{\partial p_i}{\partial z_k} = \frac{0 \cdot v - e^{z_i} \cdot e^{z_k}}{v^2} = -\left( \frac{e^{z_i}}{v} \right) \left( \frac{e^{z_k}}{v} \right) = -p_i p_k
$$

*CQFD.*

### Corollaire : le gradient de l'entropie croisée vaut p − y

Le titre de cette section annonce la perte d'entropie croisée ; voici la dérivation qui manquait. Quand la bonne réponse est le token c, la perte vaut

$$
L = -\ln p_c ,
$$

que l'on écrit aussi L = −∑ᵢ yᵢ ln pᵢ avec y le vecteur « one-hot » de la bonne réponse (

$$
y_c = 1 ,
$$

les autres composantes à 0). On dérive une fonction composée, puis on remplace

$$
\partial p_c / \partial z_k
$$

par le théorème ci-dessus :

$$
\frac{\partial L}{\partial z_k} = -\frac{1}{p_c}\,\frac{\partial p_c}{\partial z_k} = -\frac{1}{p_c}\, p_c\,(\delta_{ck} - p_k) = p_k - y_k
$$

Le gradient par rapport aux logits est donc la différence entre la distribution prédite et la bonne réponse :

$$
\nabla_z L = p - y .
$$

Le facteur

$$
1/p_c
$$

du logarithme annule exactement le facteur

$$
p_c
$$

du jacobien, si bien que le gradient ne s'annule que si p ≈ y, c'est-à-dire si le modèle est sûr **et** juste ; un modèle sûr de lui mais faux reçoit au contraire un gradient proche de 1 en valeur absolue. La version avec température, (p − y)/T, et un exemple chiffré sont à l'[étape 2](<02-Softmax-Temperature-Prochain-Token.md>), démonstration, point 4.

---

## 4. Analyse de la Température T et Comportement Asymptotique

Pour contrôler le comportement d'un agent IA, on introduit un scalaire positif T > 0 appelé **Température** :

$$
p_i(T) = \frac{e^{\frac{z_i}{T}}}{\sum_{j=1}^{|V|} e^{\frac{z_j}{T}}}
$$

### Analyse des Limites Asymptotiques :

#### 1. Limite quand T → 0⁺ (Régime Déterministe / Greedy Decoding) :

Soit i\* = argmaxⱼ zⱼ l'indice du plus grand logit, supposé unique, et

$$
z_{\max} = z_{i^\star}
$$

sa valeur. L'ancienne version écrivait zₘₐₓ = argmaxⱼ zⱼ, ce qui confond l'indice et la valeur. En divisant le numérateur et le dénominateur par

$$
e^{z_{\max}/T}
$$

$$
p_i(T) = \frac{e^{\frac{z_i - z_{\max}}{T}}}{1 + \sum_{j \neq i^\star} e^{\frac{z_j - z_{\max}}{T}}}
$$

* Si i = i\*, zᵢ − zₘₐₓ = 0 ⇒ e⁰ = 1.
* Si i ≠ i\*,

$$
z_i - z_{\max} < 0 \implies \lim_{T \to 0^+} \frac{z_i - z_{\max}}{T} = -\infty \implies e^{-\infty} = 0 .
$$

* Le dénominateur tend donc vers 1 + 0 = 1, ce qui donne la limite ci-dessous. Si le maximum est partagé par r tokens, le même calcul donne 1/r à chacun d'eux (voir l'étape 2).

Par conséquent :

$$
\lim_{T \to 0^+} p_i(T) = \begin{cases} 1 & \text{si } i = \arg\max_j z_j \\ 0 & \text{sinon} \end{cases}
$$

> La distribution Softmax converge vers une **distribution d'argmax (One-Hot Vector)**. L'agent devient totalement déterministe et rigide.

#### 2. Limite quand T → ∞ (Régime Aléatoire Pur / Max-Entropie) :

$$
\lim_{T \to \infty} \frac{z_i}{T} = 0 \implies e^0 = 1
$$

Par conséquent :

$$
\lim_{T \to \infty} p_i(T) = \frac{1}{\sum_{j=1}^{|V|} 1} = \frac{1}{|V|}
$$

> La distribution converge vers une **distribution uniforme** sur le vocabulaire. L'agent génère du texte totalement incohérent (bruit blanc).

---

## 5. Cas d'Usage Réels, Déployés et Quantifiés en Entreprise

### Cas A : Agent d'Exécution de Code SQL / JSON Structuré (Régime T = 0)

#### Contexte :
Un agent d'entreprise génère des requêtes SQL strictes pour interroger une base PostgreSQL de 50 TB. Toute erreur de syntaxe SQL fait échouer le pipeline d'orchestration.

#### Analyse et Configuration :
Le logit associé au token `SELECT` a un score de

$$
z_{\text{SELECT}} = 14.2 ,
$$

tandis que `INSERT` a

$$
z_{\text{INSERT}} = 8.1 .
$$

Avec une température classique de T = 0,7 :

$$
p_{\text{SELECT}} = \frac{e^{14{,}2/0{,}7}}{e^{14{,}2/0{,}7} + e^{8{,}1/0{,}7} + \dots} .
$$

Avec ces deux seuls logits,

$$
p_{\text{SELECT}} = 0{,}999836
$$

et il reste 0,0164 % pour `INSERT` (calcul détaillé à l'étape 2) ; les autres tokens du vocabulaire, les « … » du dénominateur, ajoutent leur propre part, d'où un ordre de grandeur illustratif de 0,03 % de tokens parasites.
* Sur des millions d'appels d'agents, cette petite probabilité produit des erreurs bien réelles.

En configurant l'agent en décodage glouton (Greedy Decoding, limite T → 0) :
* La Softmax passe en limite One-Hot : la part d'erreur due au **tirage** disparaît, puisque le même token est choisi à chaque appel. L'ancienne version parlait d'une erreur « strictement nulle » : le glouton ne corrige pas une erreur du modèle lui-même, car si le logit le plus élevé désigne un mauvais token, ce token est choisi à chaque fois.
* **Ordre de grandeur illustratif, non mesuré** : un taux d'échec de parsing JSON ou SQL qui passerait de 3,2 % à presque 0 % sur 500 000 appels par jour. Seule une validation par schéma (étape 8) garantit un document valide ; et sur les modèles Claude actuels, l'API n'accepte pas le paramètre de température (étape 2).

### Cas B : Agent Créatif de Rédaction Marketing et Brainstorming (T = 0.85 + Nucleus Top-p = 0.9)

#### Contexte :
Un agent rédacteur doit générer des slogans originaux sans tomber dans les clichés répétitifs des LLM.

#### Problème :
Si T = 0, l'agent produit toujours la même phrase stéréotypée : *"Découvrez l'avenir de la technologie grâce à notre solution innovante."*

#### Implémentation du Sampling Tronqué (Top-p) :
Pour éviter le bruit absurde d'une température élevée seule, l'ingénieur applique un filtre Top-p (p = 0.9) sur la Softmax pondérée (T = 0.85) :

1. Calcul des probabilités pᵢ(T=0.85).
2. Tri décroissant des probabilités :

$$
p_{(1)} \ge p_{(2)} \ge \dots \ge p_{(|V|)} .
$$

3. Détermination du sous-ensemble minimal K tel que :

$$
\sum_{k=1}^{K} p_{(k)} \ge 0{,}90
$$

4. Renormalisation de la Softmax sur ce sous-ensemble restreint de taille K ≪ |V|.

#### Résultat (chiffres illustratifs, non mesurés) :
* **Diversité lexicale (Type-Token Ratio)** : augmentation de l'ordre de **48 %**.
* **Taux de fautes grammaticales** : maintenu sous **0,1 %** grâce à l'élimination de la queue de distribution par le Nucleus Sampling.

---

## 6. Synthèse pour l'Ingénieur IA

| Tâche de l'Agent | Température T recommandée | Technique de Sampling | Objectif Mathématique |
| --- | --- | --- | --- |
| **Génération de Code / SQL / Tool Calling** | 0.0 | Greedy (Argmax) | Minimiser l'entropie, maximiser la précision syntaxique. |
| **Agent RAG / Synthèse de documents** | 0.1 − 0.2 | Top-p = 0.95 | Conserver la fidélité aux documents extraits. |
| **Agents Conversationnels / Chatbots** | 0.6 − 0.7 | Top-p = 0.90 | Équilibrer fluidité naturelle et cohérence contextuelle. |
| **Création de contenu / Brainstorming** | 0.85 − 1.0 | Top-p = 0.85, Min-P = 0.05 | Maximiser la créativité en coupant la queue de distribution bruitée. |

Ce tableau suppose un modèle dont on règle le décodage (modèle ouvert hébergé en interne, ou API qui accepte ces paramètres). Sur les modèles Claude actuels, l'API n'accepte ni `temperature`, ni `top_p`, ni `top_k` : la fiabilité des sorties structurées passe alors par les schémas stricts et les sorties structurées (étape 8).

> Fin de la lecture de l'étape 3. Le code de la section 7, en fin de fichier, contient les deux moitiés : à l'étape 3, lisez et exécutez ses parties « gradient » et « température ». Suite : [Prompts : définitions fondamentales](<04-Prompts-Definitions-Fondamentaux.md>) — étape 4. La seconde moitié du fichier, ci-dessous (MDP et Bellman), se relit à l'étape 39, après le [chapitre sur les MDP](<../07-Planification/38-Agent-et-Planification-MDP-Bellman.md>).

# 3. Processus de Décision Markovien (MDP) et Équation de Bellman

## 1. Contextualisation et Rôle dans l'Architecture Agentique

Contrairement à un simple LLM en mode "One-Shot" (qui produit une réponse immédiate à partir d'un prompt), un **Agent Autonome** (ex : ReAct, Tree of Thoughts, agents organisés en graphe d'états) opère dans un environnement dynamique en exécutant une **séquence d'actions** étalées dans le temps pour atteindre un objectif complexe.

La planification stratégique des agents s'appuie formellement sur les **Processus de Décision Markoviens (MDP)** et la théorie de l'Apprentissage par Renforcement (Reinforcement Learning - RL). 

Comprendre la formulation mathématique d'un MDP et l'Équation de Bellman permet à l'ingénieur agentique de :
* Structurer formellement le comportement d'un agent sous forme d'états, d'actions et de récompenses.
* Comprendre les algorithmes de recherche par arbre (MCTS, Tree of Thoughts) pour permettre au LLM d'évaluer la "valeur" d'un chemin de pensée avant de l'exécuter.
* Optimiser les politiques d'action des agents complexes pour éviter la sous-optimisation à court terme (comportement myope).

---

## 2. Définition Mathématique Formelle d'un MDP

Un **Processus de Décision Markovien** est défini par le 5-uplet (𝒮, 𝒜, 𝒫, ℛ, γ) :

1. 𝒮 : L'espace des **états** de l'environnement (ex: l'historique du chat, le code actuel, l'état du système de fichiers).
2. 𝒜 : L'ensemble des **actions** accessibles à l'agent (ex: exécuter une fonction Python, effectuer une recherche Google, répondre au client).
3. 𝒫 : La **matrice de transition d'état probabiliste** :

$$
\mathcal{P}(s' \mid s, a) = \mathbb{P}(S_{t+1} = s' \mid S_t = s, A_t = a)
$$

   Elle définit la probabilité de passer à l'état s' après avoir exécuté l'action a dans l'état s.
4. ℛ : La **fonction de récompense** :

$$
\mathcal{R}(s, a, s') = \mathbb{E}[R_{t+1} \mid S_t = s, A_t = a, S_{t+1} = s']
$$

5. γ ∈ [0, 1[ : Le **facteur d'actualisation (Discount Factor)**, mesurant la préférence temporelle de l'agent pour les récompenses immédiates par rapport aux récompenses futures.

### L'Hypothèse de Markov (Propriété d'Amnésie)

Un processus respecte la propriété de Markov si la distribution de probabilité de l'état futur ne dépend **que** de l'état présent et de l'action présente, et non de l'historique passé :

$$
\mathbb{P}(S_{t+1} \mid S_t, A_t, S_{t-1}, A_{t-1}, \dots, S_0, A_0) = \mathbb{P}(S_{t+1} \mid S_t, A_t)
$$

---

## 3. Démonstration Mathématique : Équation de Bellman et Théorème de Contraction de Banach

La **fonction de valeur d'état**

$$
V^\pi(s)
$$

sous une politique

$$
\pi(a \mid s) = \mathbb{P}(A_t = a \mid S_t = s)
$$

représente le gain cumulé futur espéré (Return Gₜ) à partir de l'état s :

$$
G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}
$$

$$
V^\pi(s) = \mathbb{E}_\pi [G_t \mid S_t = s]
$$

### Théorème 1 : Équation d'Évaluation de Bellman

Pour toute politique π, la fonction de valeur satisfait la relation récursive :

$$
V^\pi(s) = \sum_{a \in \mathcal{A}} \pi(a \mid s) \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^\pi(s') \right]
$$

### Démonstration Étape par Étape :

1. Séparons le premier terme de la somme infinie du Return Gₜ :

$$
G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \dots = R_{t+1} + \gamma \left( \sum_{k=0}^{\infty} \gamma^k R_{t+k+2} \right) = R_{t+1} + \gamma G_{t+1}
$$

2. Revisitons l'expression de

$$
V^\pi(s)
$$

par la loi de l'espérance conditionnelle :

$$
V^\pi(s) = \mathbb{E}_\pi [R_{t+1} + \gamma G_{t+1} \mid S_t = s] = \mathbb{E}_\pi [R_{t+1} \mid S_t = s] + \gamma \mathbb{E}_\pi [G_{t+1} \mid S_t = s]
$$

3. Développons le second terme via la loi de l'espérance totale en conditionnant sur l'état suivant Sₜ₊₁ = s' et l'action choisie Aₜ = a :

$$
\mathbb{E}_\pi [G_{t+1} \mid S_t = s] = \sum_{a \in \mathcal{A}} \pi(a \mid s) \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \mathbb{E}_\pi [G_{t+1} \mid S_{t+1} = s']
$$

4. Or, par définition,

$$
\mathbb{E}_\pi [G_{t+1} \mid S_{t+1} = s'] = V^\pi(s') .
$$

5. En réinjectant tout dans l'expression initiale, on obtient :

$$
V^\pi(s) = \sum_{a \in \mathcal{A}} \pi(a \mid s) \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V^\pi(s') \right]
$$

*CQFD.*

---

### Théorème 2 : Convergence de l'Opérateur d'Optimisation de Bellman (Théorème du Point Fixe de Banach)

L'opérateur d'optimisation de Bellman 𝒯\* défini sur l'espace vectoriel normé

$$
\mathbb{R}^{|\mathcal{S}|}
$$

muni de la norme du sup (norme infinie)

$$
\Vert{}V\Vert{}_\infty = \max_{s \in \mathcal{S}} |V(s)|
$$

par :

$$
(\mathcal{T}^* V)(s) = \max_{a \in \mathcal{A}} \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \left[ \mathcal{R}(s, a, s') + \gamma V(s') \right]
$$

est une **contraction stricte** de rapport γ.

#### Preuve de la Contraction :

Soient deux fonctions de valeur quelconques U et V.

$$
|(\mathcal{T}^* U)(s) - (\mathcal{T}^* V)(s)| = \left| \max_{a} \sum_{s'} \mathcal{P}(s' \mid s, a) [R + \gamma U(s')] - \max_{a'} \sum_{s'} \mathcal{P}(s' \mid s, a') [R + \gamma V(s')] \right|
$$

En utilisant l'inégalité

$$
|\max_x f(x) - \max_x g(x)| \le \max_x |f(x) - g(x)|
$$

$$
|(\mathcal{T}^* U)(s) - (\mathcal{T}^* V)(s)| \le \max_{a} \left| \gamma \sum_{s'} \mathcal{P}(s' \mid s, a) (U(s') - V(s')) \right|
$$

$$
\le \gamma \max_{a} \sum_{s'} \mathcal{P}(s' \mid s, a) |U(s') - V(s')|
$$

Puisque

$$
\sum_{s'} \mathcal{P}(s' \mid s, a) = 1
$$

et

$$
|U(s') - V(s')| \le \Vert{}U - V\Vert{}_\infty
$$

$$
|(\mathcal{T}^* U)(s) - (\mathcal{T}^* V)(s)| \le \gamma \Vert{}U - V\Vert{}_\infty \sum_{s'} \mathcal{P}(s' \mid s, a) = \gamma \Vert{}U - V\Vert{}_\infty
$$

Cette inégalité restant vraie pour tout s ∈ 𝒮, en prenant le maximum sur s :

$$
\Vert{}\mathcal{T}^* U - \mathcal{T}^* V\Vert{}_\infty \le \gamma \Vert{}U - V\Vert{}_\infty
$$

> **Garantie théorique fondamentale** : Puisque γ < 1, l'application 𝒯\* est une contraction stricte dans un espace de Banach complet. D'après le **Théorème du Point Fixe de Banach**, l'itération Vₖ₊₁ = 𝒯\* Vₖ converge de manière unique vers la fonction de valeur optimale V\*, indépendamment du point de départ V₀.

---

## 4. Implication Opérationnelle : Tree of Thoughts (ToT) et MCTS pour LLM

Les architectures avancées d'agents (modèles de raisonnement, Tree of Thoughts) transposent cette théorie aux LLM :

* **État s** : Le prompt actuel + la séquence de pensées déjà générées.
* **Action a** : Le prochain bloc de raisonnement (Thought step).
* **Récompense R** : Une évaluation intermédiaire (Value Prompt / Discriminateur) attribuant un score R ∈ [0, 1] à la cohérence de la pensée.
* **Le facteur d'actualisation** γ : permet à l'agent de ne pas choisir une pensée séduisante à court terme mais qui mène à un cul-de-sac logique.

---

## 5. Cas d'Usage Réels et Quantifiés en Entreprise

### Cas A : Agent de Réservation de Voyage Complexe (Multi-Escale et Contraintes Budgétaires)

#### Contexte :
Un agent autonome de voyage doit planifier un itinéraire comprenant vols, hôtels et transports locaux avec un budget strict de 2 500 USD.

#### Modélisation MDP :
* **États 𝒮** : Budget restant Bₜ, ville actuelle, temps restant.
* **Actions 𝒜** : {Réserver vol économique, Réserver vol direct premium, Réserver hôtel 3*, Réserver hôtel 5*}.
* **Récompense R** :
  * +100 si le voyage complet est réservé sans dépasser le budget.
  * −500 si le budget est dépassé à n'importe quelle étape (état absorbant d'échec).

#### Comparaison de Comportement selon γ (taux de succès illustratifs, non mesurés) :

1. **Régime Myope (γ = 0.1)** :
   L'agent choisit immédiatement des réservations bon marché de mauvaise qualité ou des vols directs chers au début sans anticiper le coût des hôtels futurs. Taux de succès de l'itinéraire : **34 %** (illustratif).

2. **Régime Visionnaire (γ = 0.95)** :
   Grâce à la prise en compte de la valeur future γ V(Sₜ₊₁), l'agent accepte de payer un peu plus cher un train au début pour garantir la disponibilité budgétaire d'un hôtel sécurisé à destination. Taux de succès de l'itinéraire : **96,4 %** (illustratif).

### Cas B : Agent Optimisateur de Déploiement Cloud (FinOps Infrastructure)

#### Contexte :
Un agent FinOps gère le scaling d'un cluster Kubernetes. Il doit éteindre et allumer des instances préemptibles (« spot ») pour réduire les coûts cloud sans altérer la latence de service.

#### Résultat (chiffres illustratifs, non mesurés) :
En remplaçant un contrôleur déterministe basé sur des règles `if/else` par un agent de planification utilisant un MDP avec algorithme Q-Learning approximatif :
* **Réduction de la facture cloud** : de l'ordre de **32,5 %** par mois (41 000 USD économisés par mois dans cet exemple).
* **Nombre de violations de SLA de latence** : divisé par **4,1** par rapport à une logique d'action réactive classique.

---

## 6. Synthèse des Bonnes Pratiques pour l'Ingénieur IA

| Composante MDP | Équivalent Architecture Agent | Risque de mauvaise conception |
| -------------------- | ----------------------------- | ------------------------------------------------------------ |
| **État s** | Contexte / Mémoire de l'Agent | Viol de la propriété de Markov si des informations critiques sont tronquées du prompt. |
| **Action a** | Tool Call / Étape de pensée | Espace d'actions trop vaste entraînant une explosion combinatoire de l'arbre de recherche. |
| **Récompense R** | Evaluator / Judge LLM | Reward Hacking (l'agent truque sa réponse pour maximiser la récompense du juge). |
| **Facteur γ** | Horizon de planification | Un γ trop faible rend l'agent incapable d'exécuter des pipelines multi-étapes. |

## 7. Du symbole au code : les deux démonstrations, avec des nombres

La première partie rejoue la dérivée de la softmax sur trois logits. La seconde rejoue le retour, une sauvegarde, puis la contraction sur un MDP à deux états. Copiez dans `fondements_softmax_bellman.py`.

### Déroulé, ligne par ligne

**`softmax`**, utilisée pour la température. `pic = max(logits)`, puis `exp((z - pic) / temperature)`, puis division par la somme. Retrancher `pic` est l'invariance par translation du cours, choisie pour que le plus grand exposant vaille 0.

**`demonstration_gradient`**, logits z = [1, 0,5, −0,3]. Ici on n'appelle pas `softmax` : on écrit le quotient u/v à la main, pour voir la dérivée sortir du quotient.

- `u = [exp(z_i)]` vaut [2,718, 1,649, 0,741].
- `v = sum(u)` vaut 5,108.
- `p = [ui / v]` vaut [0,532, 0,323, 0,145].

Cas i = k = 0, règle (u'v − uv') / v². Ici

$$
u' = v' = e^{z_0} ,
$$

parce que v contient

$$
e^{z_0}
$$

et que dériver

$$
e^{z_0}
$$

par rapport à z₀ redonne

$$
e^{z_0} .
$$

- `numerateur = u[0] * v - u[0] * u[0]` : le u × u est

$$
e^{z_0} \times e^{z_0} ,
$$

le terme qu'on retranche.
- `derivee = numerateur / (v * v)` vaut 0,248964.
- `p[0] * (1 - p[0])` vaut le même nombre. Les deux écritures du cours sont donc égales sur cet exemple, pas seulement sur le symbole.

Cas i = 0, k = 1. Le numérateur

$$
u_0 = e^{z_0}
$$

ne dépend pas de z₁, donc sa dérivée vaut 0. La dérivée de v vaut

$$
e^{z_1} .
$$

- `numerateur = 0 * v - u[0] * u[1]`, négatif.
- `derivee` vaut −0,171779, et `-p[0] * p[1]` aussi. Augmenter le logit 1 baisse la probabilité 0.

**`demonstration_temperature`**, logits [14,2, 8,1].

- À T = 0,05, diviser l'écart 6,1 par 0,05 donne un exposant de −122 sur le second logit. L'ancienne version disait que `exp` de ce nombre « vaut 0 en flottant » : c'est faux, e⁻¹²² ≈ 1,04 × 10⁻⁵³ est parfaitement représentable, puisqu'un float64 descend jusqu'à environ 10⁻³⁰⁸. En revanche, 1 + 1,04 × 10⁻⁵³ s'arrondit à 1, parce que l'écart est bien plus petit que la précision relative d'un float64 (environ 10⁻¹⁶) : la probabilité du premier logit vaut exactement 1.0, et celle du second, 1,04 × 10⁻⁵³, s'affiche 0.0 à six décimales. Un `assert` le vérifie.
- À T = 0,7, elle vaut 0,999836. Il reste 0,000164 sur le second.
- À T = 100, les deux logits divisés par 100 sont presque égaux. Les probabilités valent 0,515 et 0,485. À T = 10 000, l'`assert` exige qu'elles soient à moins de 0,001 de 0,5.

**Le MDP de Bellman.** Un seul dictionnaire `P`. Depuis l'état 0, deux branches : (0,5, R=0, reste en 0) et (0,5, R=1, va en 1). Depuis l'état 1 : (1, R=2, reste en 1). Une seule action par état, donc le `max` de T\* ne compare rien.

**Le retour Gₜ**, récompenses `[1, 0, 2, 2]`, γ = 0,9.

- La boucle `for R in reversed(recompenses)` part de la fin : `G = 0`, puis `G = 2 + 0.9 * G`, puis la même ligne avec 2, puis avec 0, puis avec 1. On replie Gₜ = Rₜ₊₁ + γ Gₜ₊₁ quatre fois. Résultat 4,078.
- `reconstruit` fait l'autre écriture, ∑ₖ γᵏ Rₜ₊ₖ₊₁ : 1 + 0,9× 0 + 0,81× 2 + 0,729× 2. Même 4,078. Les deux formes du cours sont le même nombre sur cette trajectoire.

**`T_etoile(V, gamma)`.**

- Pour chaque état, `sum(proba * (recompense + gamma * V[suivant]) ...)`.
- Départ `V = [0, 0]`. État 0 : 0,5×(0 + 0) + 0,5×(1 + 0) = 0,5. État 1 : 1×(2 + 0) = 2. C'est le tour 1 affiché, `[0.5, 2.0]`.
- Tour 2, on réinjecte ce V : l'état 1 vaut 2 + 0,9× 2 = 3,8. L'état 0 mélange l'ancien V[0] et le nouveau V[1]. On recommence. Après 200 tours depuis `[0, 0]` et depuis `[10, -10]`, `norme_inf` entre les deux listes est sous 10⁻⁸. Les deux départs se rejoignent en V\* ≈ [17,27, 20].

**`norme_inf`** vaut `max(abs(u - v) ...)`. C'est le plus grand écart, pas la moyenne. Le théorème borne ce maximum.

**La contraction**, sur U = [3, −1] et V = [0,5, 4], avant l'itération.

- `ecart_avant` vaut max(|3−0,5|, |−1−4|) = 5.
- On applique `T_etoile` une fois à chacun. `ecart_apres` vaut 4,5.
- `gamma * ecart_avant` vaut 0,9 × 5 = 4,5. L'écart a été multiplié par γ, pas par un nombre plus grand. C'est pour ça que la boucle de 200 tours finit par se rejoindre : chaque tour réduit l'écart d'au moins 10 %.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(logits, temperature)`** — Cette fonction est la balance qui répartit cent pour cent de confiance entre des candidats notés : elle reçoit une liste de logits et une température, 1 par défaut, retranche le plus grand logit à chacun pour que le plus grand exposant vaille 0, divise les écarts par la température, prend les exponentielles et les divise par leur somme. Elle renvoie la liste des probabilités, qui somment à 1 ; contrairement à la version de l'étape 2, elle ne contrôle pas la température, si bien qu'une température nulle produirait une `ZeroDivisionError`. Dans ce programme, seule `demonstration_temperature` l'appelle, sur les logits 14,2 et 8,1.

**`demonstration_gradient()`** — Celle-ci refait au tableau noir, sans aucun raccourci, la dérivée de la softmax, comme un professeur qui écrit chaque ligne du calcul devant la classe : elle ne reçoit rien, fixe les logits 1, 0,5 et −0,3, calcule à la main les exponentielles u, leur somme v et les probabilités p = u/v, puis applique la règle du quotient (u′v − uv′)/v² dans deux cas. Pour i = k = 0, elle trouve 0,248964, égal à p₀(1 − p₀) ; pour i = 0 et k = 1, elle trouve −0,171779, égal à −p₀p₁. Elle imprime ces lignes, vérifie chaque égalité par un `assert` à 10⁻¹² près et ne renvoie rien.

**`demonstration_temperature()`** — Cette fonction promène un thermostat sur deux logits, 14,2 et 8,1, comme un météorologue qui relève la même scène par grand froid et par canicule : elle ne reçoit rien, imprime la distribution à T = 0,05, 0,7, 5 et 100, puis vérifie les deux limites, presque toute la masse sur le premier logit à T = 0,01 et deux probabilités à moins de 0,001 de 0,5 à T = 10 000. Elle contrôle aussi la valeur 0,999836 à T = 0,7 et le cas T = 0,05, où la première probabilité vaut exactement 1.0 alors que la seconde reste strictement positive, puisque e⁻¹²² n'est pas nul mais disparaît dans l'addition 1 + e⁻¹²². Elle ne renvoie rien.

**`T_etoile(V, gamma)`** — C'est l'opérateur de Bellman, joué ici par un notaire qui réévalue chaque domaine d'après ce que rapportent ses voisins : la fonction reçoit une liste V de deux valeurs, une par état, et le facteur γ, puis, pour l'état 0 puis l'état 1, additionne sur chaque transition du dictionnaire `P` la probabilité multipliée par la récompense augmentée de γ fois la valeur de l'état d'arrivée. Comme chaque état n'a qu'une action, le maximum de la formule ne compare rien. Elle renvoie la nouvelle liste de deux valeurs : partant de V = (0, 0) avec γ = 0,9, elle donne (0,5 ; 2) au premier tour et (1,625 ; 3,8) au deuxième.

**`norme_inf(U, V)`** — Cette petite fonction est le géomètre qui ne retient que le pire écart : elle reçoit deux listes de même longueur, calcule la valeur absolue de la différence case par case et renvoie la plus grande, la norme infinie de la démonstration, et non une moyenne. Elle ne lève rien sur des listes non vides. Sur U = (3 ; −1) et V = (0,5 ; 4), elle renvoie 5, le plus grand des deux écarts 2,5 et 5, et `demonstration_bellman` s'en sert à la fois pour vérifier que deux départs différents se rejoignent à 10⁻⁸ près et pour mesurer la contraction.

**`demonstration_bellman()`** — Celle-ci raconte en trois tableaux l'histoire de la valeur d'un état, avec γ = 0,9 : elle calcule d'abord le retour de la trajectoire de récompenses 1, 0, 2 et 2, en le repliant depuis la fin puis en sommant les γᵏ Rₖ, et vérifie que les deux écritures donnent 4,078. Elle applique ensuite cinq fois `T_etoile` depuis (0, 0) en imprimant chaque tour, puis lance deux suites de 200 tours depuis (0, 0) et depuis (10 ; −10), qui se rejoignent au même V* ≈ (17,2727 ; 20), c'est-à-dire 9,5 / 0,55 et 20. Enfin, sur U = (3 ; −1) et V = (0,5 ; 4), elle montre qu'une sauvegarde fait passer l'écart de 5 à 4,5, exactement γ fois l'écart de départ ; elle ne renvoie rien et s'appuie sur ses `assert`.

**`main()`** — C'est le présentateur qui annonce les trois numéros dans l'ordre du chapitre : il appelle `demonstration_gradient`, puis `demonstration_temperature`, puis `demonstration_bellman`, sans rien leur passer ni rien récupérer, chacune portant ses propres `assert`. Si l'une d'elles échoue, l'`AssertionError` interrompt le spectacle avant la fin ; sinon il imprime une ligne qui résume ce qui a été vérifié, le quotient, les limites en température et la contraction d'un facteur γ, puis la ligne « OK — toutes les vérifications sont passées. » que le harnais du cours attend.

```python
"""Fondements LLM — jacobien de la softmax, limites en T, contraction de Bellman."""
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def softmax(logits, temperature=1.0):
    pic = max(logits)
    expo = [math.exp((z - pic) / temperature) for z in logits]
    total = sum(expo)
    return [e / total for e in expo]


# --- Démonstration du gradient, sur trois logits, pas à pas ----------------------

def demonstration_gradient():
    z = [1.0, 0.5, -0.3]
    print("=== Gradient de la softmax, z =", z)
    u = [math.exp(zi) for zi in z]
    v = sum(u)
    p = [ui / v for ui in u]
    print(f"  u = exp(z) = {[round(ui, 4) for ui in u]}")
    print(f"  v = Σ u    = {v:.4f}")
    print(f"  p = u/v    = {[round(pi, 4) for pi in p]}")

    i = 0
    # Cas i = k. (u' v − u v') / v² avec u' = v' = exp(z_i)
    numerateur = u[i] * v - u[i] * u[i]
    derivee = numerateur / (v * v)
    print(f"\n  cas i = k = 0")
    print(f"    (e^z · v − e^z · e^z) / v² = {derivee:.6f}")
    print(f"    p(1 − p)                   = {p[i] * (1 - p[i]):.6f}")
    assert abs(derivee - p[i] * (1.0 - p[i])) < 1e-12
    assert round(derivee, 6) == 0.248964

    k = 1
    # Cas i ≠ k. u ne dépend pas de z_k, v' = exp(z_k)
    numerateur = 0.0 * v - u[i] * u[k]
    derivee = numerateur / (v * v)
    print(f"\n  cas i = 0, k = 1")
    print(f"    (0 · v − e^{{z_i}} e^{{z_k}}) / v² = {derivee:.6f}")
    print(f"    −p_i p_k                         = {-p[i] * p[k]:.6f}")
    assert abs(derivee - (-p[i] * p[k])) < 1e-12
    assert round(derivee, 6) == -0.171779


def demonstration_temperature():
    print("\n=== Limites de la température, deux logits 14,2 et 8,1 ===")
    z = [14.2, 8.1]
    for T in (0.05, 0.7, 5.0, 100.0):
        p = softmax(z, temperature=T)
        print(f"  T = {T:7.2f}   P = {[round(pi, 6) for pi in p]}")
    froid = softmax(z, temperature=0.01)
    chaud = softmax(z, temperature=10_000.0)
    assert froid[0] > 1.0 - 1e-6
    assert all(abs(pi - 0.5) < 1e-3 for pi in chaud)
    assert round(softmax(z, temperature=0.7)[0], 6) == 0.999836
    tres_froid = softmax(z, temperature=0.05)
    assert tres_froid[0] == 1.0 and tres_froid[1] > 0.0   # e^-122 n'est pas nul, mais 1 + e^-122 s'arrondit à 1


# --- Bellman : retour, sauvegarde, contraction ---------------------------------

# Deux états, une action chacun. Assez petit pour imprimer chaque terme.
# s = 0 : 50 % de rester (R = 0), 50 % d'aller en 1 (R = 1)
# s = 1 : certain de rester (R = 2)
P = {
    0: [(0.5, 0.0, 0), (0.5, 1.0, 1)],
    1: [(1.0, 2.0, 1)],
}


def T_etoile(V, gamma):
    """(T* V)(s) = max_a Σ P(s'|s,a) [R + γ V(s')]. Ici une seule action, le max est trivial."""
    sortie = []
    for s in (0, 1):
        sortie.append(sum(proba * (recompense + gamma * V[suivant]) for proba, recompense, suivant in P[s]))
    return sortie


def norme_inf(U, V):
    return max(abs(u - v) for u, v in zip(U, V))


def demonstration_bellman():
    gamma = 0.9
    print("\n=== G_t = R_{t+1} + γ G_{t+1}, sur une trajectoire de 4 pas ===")
    recompenses = [1.0, 0.0, 2.0, 2.0]
    # On coupe après le 4e pas : le reste du retour est ignoré, pour pouvoir calculer à la main.
    G = 0.0
    for R in reversed(recompenses):
        G = R + gamma * G
    reconstruit = 0.0
    for k, R in enumerate(recompenses):
        reconstruit += (gamma ** k) * R
    print(f"  somme Σ γ^k R = {reconstruit:.4f}")
    print(f"  récurrence depuis la fin = {G:.4f}")
    assert abs(G - reconstruit) < 1e-12 and abs(G - 4.078) < 1e-12

    print("\n=== Une sauvegarde T* , terme à terme, V = [0, 0] puis jusqu'au point fixe ===")
    V = [0.0, 0.0]
    for tour in range(1, 6):
        V = T_etoile(V, gamma)
        print(f"  tour {tour}  V = {[round(v, 4) for v in V]}")
    # Point fixe : on itère encore. Banach garantit l'unicité.
    A = [0.0, 0.0]
    B = [10.0, -10.0]
    for _ in range(200):
        A, B = T_etoile(A, gamma), T_etoile(B, gamma)
    assert norme_inf(A, B) < 1e-8
    assert abs(A[0] - 9.5 / 0.55) < 1e-6 and abs(A[1] - 20.0) < 1e-6   # V* = [17.2727, 20]
    print(f"  deux départs différents aboutissent au même V* ≈ {[round(v, 4) for v in A]}")

    print("\n=== La contraction : ||T*U − T*V||∞ ≤ γ ||U − V||∞ ===")
    U = [3.0, -1.0]
    V = [0.5, 4.0]
    ecart_avant = norme_inf(U, V)
    ecart_apres = norme_inf(T_etoile(U, gamma), T_etoile(V, gamma))
    print(f"  ||U − V||∞ = {ecart_avant:.4f}")
    print(f"  ||T*U − T*V||∞ = {ecart_apres:.4f}")
    print(f"  γ × ||U − V||∞ = {gamma * ecart_avant:.4f}")
    assert ecart_apres <= gamma * ecart_avant + 1e-12
    assert abs(ecart_avant - 5.0) < 1e-12 and abs(ecart_apres - 4.5) < 1e-12


def main():
    demonstration_gradient()
    demonstration_temperature()
    demonstration_bellman()
    print("Quotient, limites en T, et contraction d'un facteur γ : vérifiés.")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
  p = u/v    = [0.5322, 0.3228, 0.145]
…
    (e^z · v − e^z · e^z) / v² = 0.248964
…
    (0 · v − e^{z_i} e^{z_k}) / v² = -0.171779
…
  T =    0.05   P = [1.0, 0.0]
  T =    0.70   P = [0.999836, 0.000164]
…
  récurrence depuis la fin = 4.0780
…
  tour 1  V = [0.5, 2.0]
  tour 2  V = [1.625, 3.8]
…
  deux départs différents aboutissent au même V* ≈ [17.2727, 20.0]
…
  ||T*U − T*V||∞ = 4.5000
  γ × ||U − V||∞ = 4.5000
…
OK — toutes les vérifications sont passées.
```

La contraction est la raison pour laquelle une boucle `V = T*(V)` est un algorithme et pas un vœu. Le facteur γ < 1 force deux estimations, même très différentes au départ, à se rejoindre. Sans lui, itérer la sauvegarde ne donnerait pas une valeur unique, et deux lancements du même agent de planification pourraient ne jamais tomber d'accord.

> Suite : [Coût A\*](<../07-Planification/40-Planification-Formule-A-Star.md>) — étape 40.

## Squelette algorithmique

Le programme de ce fichier vérifie trois résultats : le gradient de la perte d'entropie croisée vaut p − y, la température aplatit ou concentre la distribution, et l'opérateur de Bellman est une contraction, ce qui fait converger l'itération sur les valeurs (étape 39). Les deux algorithmes ci-dessous en sont le cœur.

```text
ALGORITHME GradientEntropieCroisée
ENTRÉES : logits z, indice c du bon token, température T
SORTIE  : la perte L et son gradient g

  p ← softmax(z / T)                       (avec soustraction du maximum)
  L ← −ln p_c
  POUR i DE 1 À |V| FAIRE
      gᵢ ← (pᵢ − 1 si i = c, sinon pᵢ) / T
  FIN POUR
  RETOURNER L, g

ALGORITHME ItérationSurLesValeurs
ENTRÉES : états S, actions A, transitions P(s′ | s, a), récompenses R(s, a), γ ∈ [0 ; 1[, tolérance ε
SORTIE  : V*, la valeur optimale

  V ← 0 pour chaque état
  RÉPÉTER
      POUR CHAQUE s DANS S FAIRE
          V′(s) ← maxₐ [ R(s, a) + γ × Σ sur s′ P(s′ | s, a) × V(s′) ]      (opérateur T*)
      FIN POUR
      écart ← maxₛ | V′(s) − V(s) |                                      (norme infinie)
      V ← V′
  JUSQU'À écart < ε
  RETOURNER V
```

**Complexité.** Le gradient coûte O(|V|) : une softmax et une soustraction par coordonnée, ce qui est bien moins que le jacobien complet O(|V|²). Une itération de Bellman coûte O(|S|² × |A|), car chaque état examine chaque action et chaque état d'arrivée. Comme T* contracte la norme infinie d'un facteur γ, l'écart à V* est multiplié par au plus γ à chaque tour : il faut de l'ordre de ln(1/ε) / ln(1/γ) itérations, soit environ 44 tours pour γ = 0,9 et ε = 0,01 en partant d'un écart de 1.

**Du squelette au code.** `GradientEntropieCroisée` correspond à `softmax` et à `demonstration_gradient`, qui compare p − y à une dérivée numérique ; `demonstration_temperature` fait varier T dans la première ligne. `ItérationSurLesValeurs` correspond à `T_etoile` (le calcul de V′), à `norme_inf` (l'écart) et à `demonstration_bellman`. Cette dernière calcule d'abord le retour Gₜ d'une trajectoire de quatre pas par la récurrence Gₜ = Rₜ₊₁ + γ Gₜ₊₁ en partant de la fin, puis applique T* cinq fois depuis V = [0 ; 0], puis 200 fois depuis deux points de départ éloignés, et vérifie qu'ils aboutissent au même V* : c'est la contraction en action.

