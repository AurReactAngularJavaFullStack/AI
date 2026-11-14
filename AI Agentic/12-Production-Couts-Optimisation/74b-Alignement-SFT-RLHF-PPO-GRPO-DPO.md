# Étape 74 bis — Optimisation — Alignement : SFT, RLHF, PPO, GRPO, DPO

**Dossier :** 12-Production-Couts-Optimisation

> Étape 74 bis du parcours · Prérequis : [Optimiseur Adam](<74-Optimiseur-Adam.md>) · Suite : [Optimisation : formules manquantes](<75-Optimisation-Formules.md>)

**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 74b-Alignement-SFT-RLHF-PPO-GRPO-DPO.md

## Définition

Un modèle pré-entraîné sait prolonger un texte ; il ne sait pas encore suivre une consigne, appeler un outil au bon moment ni préférer la réponse qu'un expert jugerait meilleure. **L'alignement** est la suite d'entraînements qui lui apprend ces comportements.

1. **Le SFT** (*supervised fine-tuning*, ajustement supervisé) entraîne le modèle sur des conversations modèles, mises en forme par un gabarit de chat. La perte d'entropie croisée n'est comptée que sur les tokens de l'assistant.
2. **Le modèle de récompense** apprend, à partir de paires « réponse préférée, réponse rejetée », à noter une réponse. C'est le modèle de Bradley-Terry.
3. **Le RLHF** (*reinforcement learning from human feedback*) pousse ensuite la politique, c'est-à-dire le modèle vu comme une loi de probabilité sur les réponses, vers les réponses bien notées. Une pénalité de KL l'empêche de trop s'éloigner du modèle de référence. **PPO** réalise cette étape avec un réseau de valeur ; **GRPO** remplace ce réseau par la moyenne d'un groupe de réponses.
4. **DPO** (*direct preference optimization*) saute le modèle de récompense et l'apprentissage par renforcement. Une identité exacte entre récompense et politique optimale transforme le problème en une simple classification des paires.

## Rôle dans un agent

Comme la descente de gradient (étape 73) et Adam (étape 74), l'alignement ne tourne pas pendant la boucle percevoir → décider → agir → observer. Il se fait hors ligne, et il façonne le composant qui **décide**. Un développeur d'agents s'en sert dans trois situations :

- **Pour spécialiser un petit modèle**, routeur, extracteur ou appelant d'outils : il fait un SFT masqué sur des traces d'agent, appels d'outils compris, souvent avec LoRA (étape 73) et AdamW (étape 74).
- **Pour corriger le style ou les choix du modèle** : il applique DPO à des paires collectées en production, quand un expert corrige une réponse.
- **Pour entraîner un comportement vérifiable** (un test qui passe, un schéma respecté, un montant exact) : il applique GRPO. Le contrôle automatique donne directement la récompense, et les N réponses tirées par question sont celles du best-of-N de l'[étape 72 quinquies](<72e-Budget-de-Raisonnement.md>).

Dans les trois cas, le modèle de référence et la pénalité de KL protègent ce que le modèle savait déjà faire.

## Équation complète

Perte SFT masquée, sur une séquence de n tokens, où m_t vaut 1 si le token x_t appartient à la réponse de l'assistant :

$$
\mathcal{L}_{SFT}(\theta) = -\frac{1}{\sum_{t=1}^{n} m_t} \sum_{t=1}^{n} m_t \,\ln \pi_\theta(x_t \mid x_{<t})
$$

$$
\frac{\partial \mathcal{L}_{SFT}}{\partial z_{t,j}} = \frac{m_t\,\bigl(p_{t,j} - y_{t,j}\bigr)}{\sum_{s=1}^{n} m_s}
$$

Modèle de récompense de Bradley-Terry et sa perte :

$$
P(y_w \succ y_l \mid x) = \sigma\bigl(r_\phi(x, y_w) - r_\phi(x, y_l)\bigr), \qquad \sigma(u) = \frac{1}{1 + e^{-u}}
$$

$$
\mathcal{L}_{RM}(\phi) = -\ln \sigma\bigl(r_\phi(x, y_w) - r_\phi(x, y_l)\bigr)
$$

Objectif du RLHF :

$$
J(\pi) = \mathbb{E}_{y \sim \pi(\cdot \mid x)}\bigl[r(x, y)\bigr] - \beta\, D_{KL}\bigl(\pi(\cdot \mid x) \parallel \pi_{ref}(\cdot \mid x)\bigr)
$$

PPO, objectif écrêté (à maximiser) :

$$
\rho(\theta) = \frac{\pi_\theta(y \mid x)}{\pi_{old}(y \mid x)}, \qquad \mathcal{L}^{CLIP}(\theta) = \mathbb{E}\Bigl[\min\bigl(\rho(\theta)\,A,\; \operatorname{clip}\bigl(\rho(\theta), 1 - \epsilon, 1 + \epsilon\bigr)\,A\bigr)\Bigr]
$$

GRPO, avantage relatif au groupe de G réponses à une même question, puis objectif :

$$
A_i = \frac{r_i - \bar{r}}{s_r}, \qquad \bar{r} = \frac{1}{G}\sum_{j=1}^{G} r_j, \qquad s_r = \sqrt{\frac{1}{G}\sum_{j=1}^{G} \bigl(r_j - \bar{r}\bigr)^2}
$$

$$
J_{GRPO}(\theta) = \frac{1}{G}\sum_{i=1}^{G} \min\bigl(\rho_i A_i,\; \operatorname{clip}(\rho_i, 1-\epsilon, 1+\epsilon)\, A_i\bigr) - \beta\, D_{KL}\bigl(\pi_\theta \parallel \pi_{ref}\bigr)
$$

Politique optimale du RLHF, et récompense qu'on en déduit :

$$
\pi^*(y \mid x) = \frac{1}{Z(x)}\, \pi_{ref}(y \mid x)\, \exp\Bigl(\frac{r(x, y)}{\beta}\Bigr), \qquad Z(x) = \sum_{y} \pi_{ref}(y \mid x)\, \exp\Bigl(\frac{r(x, y)}{\beta}\Bigr)
$$

$$
r(x, y) = \beta \ln \frac{\pi^*(y \mid x)}{\pi_{ref}(y \mid x)} + \beta \ln Z(x)
$$

DPO, marge, perte et gradient :

$$
h_\theta = \beta \Bigl[\ln \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \ln \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)}\Bigr], \qquad \mathcal{L}_{DPO}(\theta) = -\ln \sigma(h_\theta)
$$

$$
\nabla_\theta \mathcal{L}_{DPO} = -\beta\, \sigma(-h_\theta)\, \bigl[\nabla_\theta \ln \pi_\theta(y_w \mid x) - \nabla_\theta \ln \pi_\theta(y_l \mid x)\bigr]
$$

Log-probabilité d'une réponse entière : la somme ne porte que sur les tokens de la réponse, avec le même masque que le SFT.

$$
\ln \pi_\theta(y \mid x) = \sum_{t \in y} \ln \pi_\theta(y_t \mid x, y_{<t})
$$

## Décryptage des symboles

$$
x,\; y
$$

**Sens :** le prompt (système et utilisateur) et une réponse de l'assistant · **Type / plage :** suites de tokens · **Variable Python :** une réponse est un indice 0, 1 ou 2 (A, B, C) dans la politique jouet

$$
x_t,\; m_t,\; n
$$

**Sens :** le token de rang t de la conversation aplatie ; son masque, qui vaut 1 s'il appartient à la réponse de l'assistant (balise de fin comprise) et 0 sinon ; la longueur de la séquence · **Type / plage :** token, 0 ou 1, entier ≥ 1 · **Variable Python :** `tokens`, `masque`, `len(cibles)`

$$
z_{t,j},\; p_{t,j},\; y_{t,j}
$$

**Sens :** logit du token j à la position t, sa probabilité après softmax (étape 2), et le vecteur « one-hot » de la bonne cible · **Type / plage :** réel, réel dans ]0, 1[, 0 ou 1 · **Variable Python :** `logits[t][j]`, `softmax(z)[j]`, `1.0 if j == c else 0.0`

$$
\theta,\; \pi_\theta
$$

**Sens :** les paramètres du modèle entraîné, et la politique qu'ils définissent : la loi des réponses sachant le prompt · **Type / plage :** vecteur de réels ; loi de probabilité · **Variable Python :** les logits `z` de la politique jouet, et `softmax(z)`

$$
\pi_{ref},\; \pi_{old}
$$

**Sens :** la politique de référence, gelée (en général le modèle après SFT), et la politique qui a produit le lot de réponses en cours (PPO, GRPO) · **Type / plage :** lois de probabilité · **Variable Python :** `pi_ref`, `z_ref`, `z_old`

$$
y_w,\; y_l
$$

**Sens :** la réponse préférée (*winner*) et la réponse rejetée (*loser*) d'une paire · **Type / plage :** réponses · **Variable Python :** `w_`, `l_`

$$
r_\phi(x, y),\; \phi
$$

**Sens :** la récompense donnée par le modèle de récompense, et ses paramètres. Seules les différences de récompense ont un sens · **Type / plage :** réel · **Variable Python :** `r_w`, `r_l`, `r`

$$
\sigma
$$

**Sens :** la fonction sigmoïde, qui transforme un écart de récompense en probabilité de préférence · **Type / plage :** de ℝ dans ]0, 1[ · **Variable Python :** `sigmoide(x)`, et `log_sigmoide(x)` pour son logarithme

$$
\beta
$$

**Sens :** coefficient de la pénalité de KL (RLHF, GRPO) et échelle de la marge DPO. Ce n'est pas le β₁ ou le β₂ d'Adam (étape 74) · **Type / plage :** réel > 0 · **Variable Python :** `beta`, `beta_dpo`

$$
D_{KL}(\pi \parallel \pi_{ref})
$$

**Sens :** divergence de Kullback-Leibler de l'étape 50 : ce que la politique a perdu de vue de la référence · **Type / plage :** réel ≥ 0 · **Variable Python :** `kl(p, q)`

$$
J(\pi)
$$

**Sens :** objectif du RLHF : récompense moyenne moins le coût d'éloignement · **Type / plage :** réel · **Variable Python :** `objectif_rlhf(pi, pi_ref, r, beta)`

$$
\rho,\; A,\; \epsilon
$$

**Sens :** le rapport de probabilité entre la politique entraînée et celle qui a généré le lot ; l'avantage, c'est-à-dire de combien la réponse a fait mieux que prévu ; la demi-largeur de la zone de confiance de PPO. Ce ε n'est pas celui d'Adam, et ce ρ n'est pas le taux d'utilisation des files d'attente (étape 69) · **Type / plage :** réel > 0, réel, réel dans ]0, 1[ (0,2 en général) · **Variable Python :** `rho`, `avantage`, `eps`

$$
G,\; r_i,\; \bar{r},\; s_r,\; A_i
$$

**Sens :** la taille du groupe GRPO, la récompense de la i-ième réponse, la moyenne et l'écart-type (sur G, pas G − 1) du groupe, et l'avantage normalisé · **Type / plage :** entier ≥ 2, réels · **Variable Python :** `g`, `recompenses`, `moyenne`, `ecart`, `avantages_grpo(...)`

$$
\pi^*,\; Z(x)
$$

**Sens :** la politique qui maximise J, et sa constante de normalisation, une somme sur toutes les réponses possibles, incalculable pour un vrai LLM · **Type / plage :** loi de probabilité, réel > 0 · **Variable Python :** `politique_optimale(pi_ref, r, beta)` renvoie `(pi_opt, z_part)`

$$
h_\theta
$$

**Sens :** marge DPO : de combien la politique a relevé la réponse préférée par rapport à la rejetée, comparée à la référence, multipliée par β · **Type / plage :** réel · **Variable Python :** `marge_dpo(z, z_ref, w, l, beta)`

## Démonstration

### 1. SFT : un token masqué ne contribue pas au gradient

L'étape 2 a montré que le gradient de −ln p_c par rapport aux logits vaut p − y. La perte SFT est une somme pondérée de tels termes, un par position. Les logits z_t de la position t n'apparaissent que dans le terme t, d'où

$$
\frac{\partial \mathcal{L}_{SFT}}{\partial z_t} = \frac{m_t\,(p_t - y_t)}{\sum_s m_s}
$$

Si m_t = 0, cette dérivée est exactement nulle : quoi que le modèle prédise à une position du message utilisateur, la perte ne change pas. Dans le code, on ajoute +5 à la moitié des logits de la position « plafond », qui appartient au message de l'utilisateur. La perte reste strictement égale à 2,5112, et la dérivée analytique en une position apprise coïncide avec les différences finies.

**Pourquoi masquer ?** Pour trois raisons :

- **Le rôle du modèle est de répondre.** Il n'a pas à imiter l'utilisateur ni à réécrire le prompt système.
- **Le prompt est souvent plus long que la réponse.** Dans l'exemple, 7 des 12 positions sont du prompt : sans masque, plus de la moitié du signal servirait à imiter le prompt. Les deux pertes calculées (2,5112 avec masque, 2,8618 sans) ne mesurent pas la même chose.
- **La balise de fin doit être apprise.** Elle fait partie du masque, sinon le modèle n'apprend jamais à s'arrêter.

**Normaliser par le bon nombre.** On divise par Σ m_t (5 tokens appris), et non par le nombre de positions (12) : sinon, l'échelle de la perte dépendrait de la longueur du prompt.

**Ce que le masque ne fait pas.** Un gradient nul sur les logits des positions masquées ne veut pas dire que le texte de l'utilisateur est sans influence. Il reste le contexte que l'attention lit, et le gradient des positions apprises traverse ses représentations. Le modèle n'apprend pas à **produire** le texte de l'utilisateur, mais il apprend à partir de lui. Le masque n'est donc pas une anonymisation.

**Le gabarit de chat.** Chaque famille de modèles a son propre gabarit de rôles, avec ses balises spéciales. Il faut utiliser à l'inférence exactement celui de l'entraînement. Les balises de rôle (`<assistant>` ici) font partie du prompt et ont le masque 0.

### 2. Le modèle de récompense de Bradley-Terry

Des annotateurs comparent deux réponses à la même question. Le modèle de Bradley-Terry, étudié en détail à l'[étape 65 bis](<../10-Evaluation/65b-Classement-par-Duels-Elo-Bradley-Terry.md>), suppose que la préférée l'emporte avec la probabilité σ(r_w − r_l). Entraîner le modèle de récompense par maximum de vraisemblance revient à minimiser −ln σ(d), où d = r_w − r_l.

Deux dérivées servent dans tout le fichier. La première est celle de la sigmoïde :

$$
\sigma'(u) = \frac{e^{-u}}{(1 + e^{-u})^2} = \sigma(u)\,\bigl(1 - \sigma(u)\bigr) = \sigma(u)\,\sigma(-u)
$$

La seconde est celle du logarithme de la sigmoïde :

$$
\frac{d}{du} \ln \sigma(u) = \frac{d}{du}\Bigl(-\ln\bigl(1 + e^{-u}\bigr)\Bigr) = \frac{e^{-u}}{1 + e^{-u}} = \frac{1}{1 + e^{u}} = \sigma(-u)
$$

On a utilisé 1 − σ(u) = e⁻ᵘ / (1 + e⁻ᵘ) = σ(−u). La perte a donc pour dérivées −σ(−d) par rapport à r_w et +σ(−d) par rapport à r_l. Le gradient monte la note de la préférée et baisse celle de la rejetée, avec un poids σ(−d). Ce poids est grand quand le modèle classe mal la paire (d < 0), et petit quand il la classe déjà bien.

Remplacer r par r + c ne change rien, puisque seule la différence compte. Les récompenses ne sont donc définies qu'à une constante près, et on les recentre avant de s'en servir. Avec d = 1, on obtient σ(1) = 0,7311, une perte de 0,3133 et une dérivée de −σ(−1) = −0,2689.

### 3. L'objectif du RLHF a une solution exacte : π* ∝ π_ref · exp(r/β)

On fixe le prompt x et l'on suppose un ensemble fini de réponses. On cherche la loi π qui maximise

$$
J(\pi) = \sum_y \pi(y)\, r(y) - \beta \sum_y \pi(y) \ln\frac{\pi(y)}{\pi_{ref}(y)}
$$

On écrit r(y) = β ln(exp(r(y)/β)) et l'on met −β en facteur :

$$
J(\pi) = -\beta \sum_y \pi(y) \ln\frac{\pi(y)}{\pi_{ref}(y)\, e^{r(y)/\beta}}
$$

On introduit ensuite Z = Σ π_ref(y) exp(r(y)/β) et π* = π_ref exp(r/β) / Z, de sorte que π_ref(y) exp(r(y)/β) = Z π*(y). Comme Σ π(y) = 1, il vient :

$$
J(\pi) = -\beta \sum_y \pi(y) \ln\frac{\pi(y)}{Z\, \pi^*(y)} = \beta \ln Z - \beta\, D_{KL}(\pi \parallel \pi^*)
$$

Par l'inégalité de Gibbs, démontrée à l'[étape 50](<../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>), D_KL(π ‖ π*) ≥ 0, avec égalité si et seulement si π = π*. Donc J(π) ≤ β ln Z pour toute loi π, avec égalité seulement en π*. Le maximum existe, il est unique, et sa valeur vaut β ln Z.

**Exemple chiffré.** On prend π_ref = (0,5 ; 0,3 ; 0,2) sur les réponses A, B et C, r = (1 ; 2 ; 0) et β = 1. Les poids valent 0,5e = 1,3591 ; 0,3e² = 2,2167 ; 0,2. Donc Z = 3,7759, π* = (0,3600 ; 0,5871 ; 0,0530) et J(π*) = ln 3,7759 = 1,3286. On compare à deux politiques simples :

- **Rester sur π_ref** donne J = 0,5 + 0,6 = 1,1 : aucun coût de KL, mais moins de récompense.
- **Tout mettre sur B**, la meilleure réponse, donne la récompense maximale, mais un coût de KL de ln(1/0,3) = 1,2040, soit J = 2 − 1,2040 = 0,7960.

Le code vérifie l'identité J(π) = β ln Z − β D_KL(π ‖ π*) sur 200 lois tirées au hasard.

**L'effet de β.** Quand β → 0, π* se concentre sur la meilleure récompense : avec β = 0,1, π* = (0,0001 ; 0,9999 ; 0,0000). Quand β → ∞, π* revient à π_ref : avec β = 10, π* = (0,4938 ; 0,3275 ; 0,1787).

### 4. De la politique optimale à la perte DPO

On prend le logarithme de π* :

$$
\ln \pi^*(y) = \ln \pi_{ref}(y) + \frac{r(y)}{\beta} - \ln Z
$$

On isole r, ce qui donne r(y) = β ln(π*(y)/π_ref(y)) + β ln Z. Le terme β ln Z dépend du prompt x, mais pas de la réponse y. Dans la différence qu'utilise le modèle de Bradley-Terry, il disparaît donc :

$$
r(y_w) - r(y_l) = \beta \ln\frac{\pi^*(y_w)}{\pi_{ref}(y_w)} - \beta \ln\frac{\pi^*(y_l)}{\pi_{ref}(y_l)}
$$

La probabilité de préférence ne s'écrit plus qu'avec la politique et la référence. DPO remplace π* par la politique entraînée π_θ, puis maximise la vraisemblance des préférences observées, ce qui donne la perte −ln σ(h_θ). La politique devient ainsi son propre modèle de récompense, avec la récompense implicite β ln(π_θ/π_ref).

Il n'y a plus de Z à calculer (c'était une somme sur toutes les réponses possibles), plus de génération pendant l'entraînement, plus d'apprentissage par renforcement : seulement quatre log-probabilités par paire.

### 5. Un pas de DPO augmente la probabilité de la réponse préférée

La règle de dérivation en chaîne donne le gradient de l'équation complète. On utilise la dérivée de −ln σ(h), qui vaut −σ(−h) (point 2), et le fait que π_ref est gelé.

Pour une politique jouet qui est une softmax de logits z sur trois réponses, on a ∇_z ln π(y) = e_y − π, où e_y est le vecteur « one-hot » de y : c'est le résultat p − y de l'étape 2, au signe près. Les termes en π s'annulent :

$$
\nabla_z \mathcal{L}_{DPO} = -\beta\,\sigma(-h)\,\bigl[(e_w - \pi) - (e_l - \pi)\bigr] = -\beta\,\sigma(-h)\,(e_w - e_l)
$$

Le gradient ne touche que les logits de y_w et de y_l. Un pas de descente z′ = z − η∇ ajoute δ = η β σ(−h) > 0 au logit de la préférée et retire δ à celui de la rejetée. On écrit la nouvelle probabilité de y_w en divisant numérateur et dénominateur par son exponentielle :

$$
\pi'(y_w) = \frac{1}{1 + e^{\,z_l - z_w - 2\delta} + \sum_{k \ne w, l} e^{\,z_k - z_w - \delta}}
$$

Chaque terme du dénominateur décroît strictement quand δ augmente, donc π′(y_w) > π(y_w). Le même calcul, mené pour y_l, montre que π′(y_l) < π(y_l).

**La troisième réponse.** Le gradient ne la touche pas, mais sa probabilité change par la normalisation. Le dénominateur de la softmax varie de

$$
e^{z_w}\bigl(e^{\delta} - 1\bigr) + e^{z_l}\bigl(e^{-\delta} - 1\bigr)
$$

Dans l'exemple, cela fait 0,3 × 0,1052 − 0,5 × 0,0952 = 0,0316 − 0,0476 < 0. Le dénominateur baisse, donc π(C) monte, de 0,2 à 0,2033.

**Et pour un vrai LLM ?** Les paramètres sont partagés entre toutes les réponses, et la garantie ne porte plus que sur la marge h, au premier ordre. La log-probabilité de la préférée peut elle-même baisser, si celle de la rejetée baisse davantage (voir les pièges).

### 6. Avec des préférences de Bradley-Terry, DPO retrouve exactement π*

On suppose que les préférences sont produites par le modèle de Bradley-Terry avec une vraie récompense r*. La réponse i est alors préférée à j avec la probabilité q_ij = σ(r*_i − r*_j).

**La marge s'écrit simplement.** Pour la politique jouet, on note u = z − z_ref. Le terme de log-somme-exponentielle de la softmax s'annule dans la différence, et la marge vaut h_ij = β(u_i − u_j).

**La perte moyenne est convexe.** Elle s'écrit Σ q_ij ℓ(β(u_i − u_j)), sur les couples i ≠ j, avec ℓ(h) = −ln σ(h). La fonction ℓ est convexe, puisque ℓ″(h) = σ(h) σ(−h) > 0 (point 2). Composée avec une application linéaire de u, elle le reste. Tout point où le gradient s'annule est donc un minimum global.

**Le gradient s'annule exactement en π*.** Le gradient vaut

$$
\frac{\partial \mathcal{L}}{\partial u_i} = \beta \sum_{j \ne i} \Bigl(\sigma\bigl(\beta (u_i - u_j)\bigr) - q_{ij}\Bigr)
$$

et il s'annule quand β(u_i − u_j) = r*_i − r*_j pour toutes les paires, c'est-à-dire quand u = r*/β + c. Alors π_θ ∝ π_ref exp(u) ∝ π_ref exp(r*/β) : c'est exactement l'optimum du RLHF (point 3), atteint sans modèle de récompense ni apprentissage par renforcement.

Avec r* = (0 ; 1 ; −1) et β = 0,5, π* vaut (0,1822 ; 0,8079 ; 0,0099). Trois mille pas de descente, partis de π_ref, retrouvent ces valeurs à 10⁻⁶ près.

### 7. PPO : l'écrêtage borne le gain de chaque échantillon

Le gradient de politique augmente π(y) pour les réponses d'avantage A > 0 (meilleures que prévu) et la diminue pour A < 0. PPO estime A avec un réseau de valeur V_ψ(x), le critique ; dans un problème à une seule étape comme celui-ci, A = r − V(x). Pour économiser les générations, PPO réutilise le même lot pendant plusieurs passes, et le rapport ρ = π_θ/π_old s'éloigne alors de 1.

L'objectif écrêté se simplifie selon le signe de A :

- **Si A > 0**, min(ρA, clip(ρ)A) = A min(ρ, clip(ρ)) = A min(ρ, 1 + ε). En effet, sous 1 − ε, l'écrêtage remonte ρ à 1 − ε > ρ et le min garde ρ ; dans l'intervalle, les deux termes sont égaux ; au-dessus de 1 + ε, l'écrêtage ramène à 1 + ε < ρ.
- **Si A < 0**, multiplier par A négatif échange min et max, et l'objectif vaut A max(ρ, 1 − ε).

On en tire trois conséquences.

**Le gain est borné.** Pour A > 0, L(ρ) − L(1) = A(min(ρ, 1 + ε) − 1) ≤ εA. Pour A < 0, max(ρ, 1 − ε) − 1 ≥ −ε, donc L(ρ) − L(1) = A(max(ρ, 1 − ε) − 1) ≤ −εA = ε|A|. Dans les deux cas :

$$
\mathcal{L}(\rho) - \mathcal{L}(1) \le \epsilon\,\lvert A \rvert \quad \text{pour tout } \rho > 0
$$

**Le gradient s'annule au-delà de la borne favorable.** Pour A > 0 et ρ > 1 + ε, l'objectif est constant : rien ne pousse plus loin. De même pour A < 0 et ρ < 1 − ε.

**L'objectif est pessimiste.** Dans la direction défavorable (A > 0 et ρ < 1 − ε, ou A < 0 et ρ > 1 + ε), il garde ρA avec tout son gradient : un mauvais mouvement est toujours corrigé.

**Exemple chiffré**, avec ε = 0,2 :

- pour A = +2, L vaut 1,00 ; 1,60 ; 2,00 ; 2,40 ; 2,40 en ρ = 0,5 ; 0,8 ; 1 ; 1,2 ; 1,5 : au-delà de 1,2, le gain plafonne à εA = 0,4 ;
- pour A = −2, L vaut −1,60 ; −1,60 ; −2,00 ; −2,40 ; −3,00 aux mêmes points.

**Une nuance qui compte en production.** Ce qui est borné, c'est le gain de l'objectif, donc l'incitation à bouger. Le rapport ρ lui-même ne l'est pas.

- Avec 60 pas de taille η = 0,05 sur la réponse C (A = +1), ρ s'arrête à 1,223, juste après la borne, et la KL vaut 0,0060. Sans écrêtage, ρ atteint 4,599 et la KL 1,2206.
- Avec η = 0,5, un seul pas fait sauter ρ de 1 à 1,577 : la borne est franchie avant que le gradient ne s'annule.

C'est pourquoi les implémentations surveillent aussi la KL entre π_θ et π_old, arrêtent les passes dès qu'elle dépasse un seuil, et gardent des pas petits.

### 8. GRPO : la moyenne du groupe remplace le réseau de valeur

Le critique de PPO est un second réseau, souvent aussi gros que la politique, qu'il faut entraîner en même temps. GRPO s'en passe (Shao et al., 2024). Pour chaque question, il tire G réponses et les note, souvent avec une récompense vérifiable : un test, une correspondance exacte (étape 64). Il prend ensuite Aᵢ = (rᵢ − r̄)/s_r.

**Les avantages sont centrés et réduits.** Quand s_r > 0, ΣAᵢ = 0 et (1/G)ΣAᵢ² = 1, par construction : on retranche la moyenne, puis on divise par l'écart-type. Dans un groupe, certaines réponses sont poussées vers le haut et les autres vers le bas : la politique apprend à faire mieux que ses propres essais, pas à atteindre un niveau absolu.

**Une référence constante ne biaise pas le gradient.** Pour toute politique,

$$
\mathbb{E}_{y \sim \pi}\bigl[\nabla \ln \pi(y)\bigr] = \sum_y \pi(y)\,\frac{\nabla \pi(y)}{\pi(y)} = \nabla \sum_y \pi(y) = \nabla 1 = 0
$$

Retrancher une constante b de la récompense ne change donc pas l'espérance du gradient E[(r − b) ∇ ln π], mais réduit sa variance. Une nuance : la moyenne du groupe dépend un peu de rᵢ lui-même, ce qui introduit un biais de l'ordre de 1/G. La version « laisser-un-de-côté » (RLOO), qui exclut la réponse i de sa propre moyenne, le supprime exactement.

**Un groupe uniforme n'apprend rien.** Si les G récompenses sont égales, s_r = 0, et le code renvoie des avantages nuls, selon la même convention que `min_max` dans le code canonique. Avec une récompense binaire de taux de succès p, un groupe est uniforme avec la probabilité pᴳ + (1 − p)ᴳ. Pour p = 0,95 et G = 8, cela fait 0,6634 : deux groupes sur trois ne donnent aucun gradient. Pour p = 0,5, cela ne fait que 0,0078. Ce sont les mêmes N réponses que le best-of-N de l'étape 72 quinquies, et l'on en tire une règle : les questions trop faciles (p ≈ 1) ou trop difficiles (p ≈ 0) ne servent à rien pour l'entraînement.

**Exemples chiffrés.**

- Le groupe (1, 0, 0, 1) a pour moyenne 0,5 et pour écart-type 0,5, d'où des avantages (+1, −1, −1, +1).
- Le groupe (1, 0, 0, 0) a pour moyenne 0,25 et pour écart-type √(0,25 × 0,75) = 0,4330, d'où (+1,7321 ; −0,5774 ; −0,5774 ; −0,5774) : le seul succès pèse trois fois chaque échec. Un succès rare est fortement récompensé.
- Sur la politique jouet, 30 pas de GRPO avec G = 8, une récompense de 1 pour la seule réponse B et β = 0,02 font passer π(B) de 0,3 à 0,9684, pour une KL de 1,0392 par rapport à la référence.

### 9. Exemple fait à la main (le code reprend ces nombres)

Un pas de DPO sur la politique jouet. π_ref = (0,5 ; 0,3 ; 0,2) sur A, B et C ; la politique part de π_ref ; la réponse préférée est B et la rejetée A ; β = 0,1 et η = 2.

| Étape du calcul | Valeur |
|---|---|
| marge initiale h, puisque π_θ = π_ref | 0 |
| perte initiale, −ln σ(0) = ln 2 | 0,6931 |
| poids σ(−h) | 0,5 |
| gradient sur (A, B, C), −0,1 × 0,5 × (e_B − e_A) | (0,05 ; −0,05 ; 0) |
| logits après le pas z − 2 × gradient | z + (−0,1 ; +0,1 ; 0) |
| poids non normalisés 0,5e⁻⁰·¹ ; 0,3e⁰·¹ ; 0,2 | 0,4524 ; 0,3316 ; 0,2 |
| nouvelle politique, après division par 0,9840 | (0,4598 ; 0,3370 ; 0,2033) |
| nouvelle marge, 0,1 × (0,1 − (−0,1)) | 0,02 |
| nouvelle perte, ln(1 + e⁻⁰·⁰²) | 0,6832 |

La log-somme-exponentielle s'annule dans la marge, qui ne dépend que de l'écart des logits. La préférée passe de 0,3 à 0,3370, la rejetée de 0,5 à 0,4598, et la troisième monte un peu, comme l'annonçait le point 5.

## Effets et comportement

- **β règle la distance à la référence.** Petit, il laisse la politique s'éloigner : plus de récompense, mais plus de risque de détournement et d'oubli. Grand, il la garde près de π_ref. Les deux limites sont visibles au point 3. En DPO, β est aussi l'échelle de la marge ; on le règle sur un jeu de validation, des valeurs de 0,1 à 0,5 étant courantes.
- **ε règle la prudence de PPO.** La valeur 0,2 de l'article d'origine (Schulman et al., 2017) reste la plus répandue. Un ε plus petit donne des pas plus sûrs mais plus nombreux.
- **DPO se dose lui-même.** Le poids σ(−h) rend presque nulles les paires déjà bien classées, et donne tout leur poids (β) aux paires mal classées.
- **Plus G est grand, meilleure est la moyenne du groupe**, et plus rares sont les groupes uniformes. Mais le coût des générations croît linéairement avec G, comme celui du best-of-N (étape 72 quinquies, point 7).
- **L'ordre des étapes compte.** On fait d'abord le SFT, et son modèle devient π_ref pour DPO ou le RLHF. Les préférences affinent un comportement qui existe déjà ; elles ne l'inventent pas.
- **La mémoire décide souvent de la méthode.** PPO garde quatre modèles en mémoire : la politique, la référence, le modèle de récompense et le critique. GRPO en garde trois, sans critique. DPO n'en garde que deux, et la référence peut même être remplacée par ses log-probabilités calculées une fois pour toutes.

## Du symbole au code Python

| Symbole | Variable ou fonction |
|---|---|
| gabarit de chat, m_t | `gabarit_chat(messages)` renvoie `(tokens, masque)` |
| perte SFT et son gradient | `perte_sft(logits, cibles, masque)`, `gradient_sft(...)` |
| σ, ln σ | `sigmoide(x)`, `log_sigmoide(x)` |
| perte de Bradley-Terry | `perte_bt(r_w, r_l)` |
| D_KL | `kl(p, q)` |
| J(π) | `objectif_rlhf(pi, pi_ref, r, beta)` |
| π*, Z | `politique_optimale(pi_ref, r, beta)` |
| objectif écrêté, sa dérivée | `objectif_ppo(rho, avantage, eps)`, `derivee_ppo(...)` |
| un pas de PPO sur une réponse | `pas_ppo(z, z_old, y, avantage, eps, eta, ecretage)` |
| Aᵢ | `avantages_grpo(recompenses)` |
| gradient de la KL | `gradient_kl(z, pi_ref)` |
| un pas de GRPO | `pas_grpo(z, pi_ref, recompense, g, beta, eta, rng)` |
| h_θ, perte et gradient DPO | `marge_dpo(...)`, `perte_dpo(...)`, `gradient_dpo(...)` |

### Déroulé, ligne par ligne

**`softmax`, `log_softmax`, `sigmoide`, `log_sigmoide`.** Ce sont les briques de l'étape 2, écrites en version stable.

- `softmax` retranche le plus grand logit avant l'exponentielle. `log_softmax` calcule la log-somme-exponentielle de la même manière.
- `sigmoide` choisit sa formule selon le signe de x, pour ne jamais calculer l'exponentielle d'un grand nombre positif.
- `log_sigmoide(x)` vaut `-math.log1p(math.exp(-x))` si x ≥ 0, et `x - math.log1p(math.exp(x))` sinon. Ainsi, ln σ(−800) vaut −800 au lieu de planter.

**`kl(p, q)`** reprend la convention de l'étape 50. Une issue où p = 0 ne compte pas. Une issue où q = 0 alors que p > 0 donne `math.inf`.

**`gabarit_chat(messages)`** aplatit une liste `(rôle, texte)` en tokens, un mot par token, et construit le masque. Chaque balise de rôle reçoit 0, chaque mot de l'assistant reçoit 1, et l'assistant reçoit en plus une balise `<fin>` de masque 1. La conversation de `main` donne 13 tokens :

```text
<system> agent crédit <user> plafond d'endettement ? <assistant> 50 % du revenu <fin>
```

Les masques valent 1 sur les cinq derniers.

**`perte_sft(logits, cibles, masque)`** calcule `-sum(m * log_softmax(z)[c] ...) / n`, avec `n = sum(masque)`. Un masque vide lève `ValueError`, puisqu'il n'y a rien à apprendre et que la division n'aurait pas de sens. Dans `main`, la position t lit le token t et prédit le token t + 1 : `cibles = tokens[1:]` et le masque est décalé de la même façon (`masque[1:]`). La position 7, qui lit `<assistant>`, doit donc prédire « 50 », et son masque vaut 1.

**`gradient_sft`** renvoie, pour chaque position, `m * (p_j - y_j) / n`. Aux positions de masque 0, chaque composante vaut exactement 0.0.

**`perte_bt(r_w, r_l)`** vaut `-log_sigmoide(r_w - r_l)`. Pour `(1.0, 0.0)`, elle vaut 0,3133 ; pour `(4.0, 3.0)` aussi.

**`objectif_rlhf(pi, pi_ref, r, beta)`** calcule Σ π r − β KL. Pour π_ref lui-même, il vaut 0,5 × 1 + 0,3 × 2 + 0,2 × 0 − 0 = 1,1.

**`politique_optimale(pi_ref, r, beta)`** calcule les poids `q * math.exp(ri / beta)`, puis les normalise. Pour l'exemple du point 3, les poids valent 1,3591 ; 2,2167 et 0,2, et Z vaut 3,7759. La garde `beta <= 0` refuse un β nul, qui diviserait par zéro.

**`objectif_ppo(rho, avantage, eps)`** écrit l'objectif écrêté tel quel : `min(rho * avantage, min(max(rho, 1 - eps), 1 + eps) * avantage)`. Le `min(max(...))` imbriqué est le clip. **`derivee_ppo`** applique le point 7 : elle renvoie A tant que la branche non écrêtée est active, et 0 sinon.

**`pas_ppo(...)`** fait un pas de montée de gradient pour une seule réponse y. On calcule ρ = π(y)/π_old(y), puis la dérivée de l'objectif par rapport à ρ, puis on multiplie par dρ/dz = ρ(e_y − π), qui vient de ∇ ln π = e_y − π. Avec `ecretage=False`, la dérivée vaut toujours A : c'est l'objectif ρA sans protection.

**`avantages_grpo(recompenses)`** calcule la moyenne et l'écart-type sur G. Si l'écart-type vaut 0.0, elle renvoie une liste de zéros, sans epsilon caché. Un groupe vide lève `ValueError`.

**`gradient_kl(z, pi_ref)`** renvoie πⱼ(ln(πⱼ/π_ref,ⱼ) − D_KL). On obtient cette formule en dérivant Σ πᵢ ln(πᵢ/qᵢ) avec ∂πᵢ/∂zⱼ = πᵢ(δᵢⱼ − πⱼ) : le « +1 » de la dérivée de x ln x disparaît, parce que Σᵢ πᵢ(δᵢⱼ − πⱼ) = 0.

**`pas_grpo(...)`** fait une itération complète :

1. il tire G réponses avec `rng.choices(..., weights=pi, k=g)` ;
2. il les note, puis calcule leurs avantages ;
3. il accumule le gradient Σ Aᵢ (e_yᵢ − π)/G ;
4. il retranche β fois le gradient de la KL, puis monte d'un pas η.

C'est le premier pas sur un lot neuf, donc ρ = 1 et l'écrêtage n'agit pas. Le générateur `rng` est passé en argument, ce qui rend la suite de tirages reproductible.

**`marge_dpo`, `perte_dpo`, `gradient_dpo`.** Ce sont les trois formules DPO de l'équation complète. `gradient_dpo` calcule séparément `grad_w = e_w − π` et `grad_l = e_l − π`, puis combine les deux. Le programme vérifie que la composante sur la troisième réponse vaut exactement 0.

**`main()`**, bloc par bloc.

1. Le gabarit donne 13 tokens et 5 cibles apprises : « 50 », « % », « du », « revenu », `<fin>`. Les logits sont tirés par `random.Random(74)`. Le programme calcule les pertes avec masque (2,5112) et sans masque (2,8618), puis vérifie trois choses : le gradient est nul hors masque, une perturbation sur la position « plafond » laisse la perte strictement identique, et la dérivée analytique en une position apprise coïncide avec les différences finies (pas `dz = 1e-6`).
2. Bradley-Terry : σ(1) = 0,7311, une perte de 0,3133, l'invariance par translation, et une dérivée −σ(−1) vérifiée par différences finies.
3. π*, Z, puis J(π*) = β ln Z > J(π_ref) = 1,1 > J(tout sur B) = 0,7960. L'identité J(π) = β ln Z − β KL(π ‖ π*) est vérifiée sur 200 lois tirées par `random.Random(740)`. Les récompenses implicites β ln(π*/π_ref) ont les mêmes différences que r. Le bloc se termine sur les deux limites de β.
4. Un pas de DPO depuis π_ref : la perte passe de ln 2 à 0,6832, et la politique devient (0,4598 ; 0,3370 ; 0,2033). Le programme vérifie que B monte, que A baisse, et que la composante du gradient sur C est nulle.
5. Trois mille pas de descente sur la perte DPO moyenne, avec les préférences de Bradley-Terry de r* = (0 ; 1 ; −1) et β = 0,5. Ils retrouvent π* à 10⁻⁶ près.
6. Le programme affiche les deux lignes de l'objectif PPO, puis vérifie la borne L(ρ) − L(1) ≤ ε|A| pour 300 valeurs de ρ entre 0,01 et 3, ainsi que les dérivées nulles ou pleines selon la branche. Il compare enfin 60 pas avec et sans écrêtage, pour deux tailles de pas.
7. Les avantages GRPO de trois groupes, avec leur moyenne nulle et leur variance unité. Suivent la probabilité d'un groupe uniforme, l'égalité E[∇ ln π] = 0 vérifiée sur une politique quelconque, puis 30 pas de GRPO tirés par `random.Random(2024)`.
8. Trois entrées invalides (groupe vide, β = 0, masque vide) doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`softmax(z)`** — Cette fonction est l'urne qui transforme des scores bruts en probabilités : elle reçoit une liste de logits, retranche le plus grand avant de prendre l'exponentielle, pour ne jamais faire déborder un grand nombre, puis divise chaque exponentielle par leur somme. Elle renvoie une distribution qui somme à 1 ; avec les logits ln 0,5, ln 0,3 et ln 0,2, elle redonne exactement la politique de référence 0,5 ; 0,3 ; 0,2, et toutes les politiques jouets du programme, de PPO à DPO, passent par elle.

**`log_softmax(z)`** — Celle-ci donne directement le logarithme des probabilités, comme un comptable qui tient ses comptes en logarithmes pour éviter les nombres trop petits : elle reçoit une liste de logits, calcule la log-somme-exponentielle en retranchant le plus grand logit, puis renvoie chaque logit diminué de cette quantité. Elle sert à la perte SFT, qui a besoin de ln π de la cible à chaque position, et à `marge_dpo`, qui compare les log-probabilités de la politique et de la référence.

**`sigmoide(x)`** — Cette fonction est le convertisseur d'un écart de score en probabilité de préférence : elle reçoit un nombre et renvoie 1/(1 + e⁻ˣ), en choisissant sa formule selon le signe de x pour ne jamais calculer l'exponentielle d'un grand nombre positif. Pour un écart de récompense de 1, elle donne 0,7311, la probabilité que la réponse préférée le soit selon Bradley-Terry ; `gradient_dpo` s'en sert pour pondérer chaque pas par σ(−h).

**`log_sigmoide(x)`** — Celle-ci calcule ln σ(x) sans jamais faire déborder l'exponentielle, comme un funambule qui change de pied selon le côté où penche la corde : elle reçoit un nombre et renvoie −ln(1 + e⁻ˣ) si x est positif ou nul, et x − ln(1 + eˣ) sinon, grâce à `math.log1p`. Ainsi ln σ(−800) vaut −800 au lieu de planter ; `perte_bt` et `perte_dpo` sont toutes deux l'opposé de cette fonction appliquée à une marge.

**`kl(p, q)`** — Cette fonction mesure en nats combien une politique s'est éloignée de sa référence, comme un géomètre qui note l'écart entre deux cartes du même terrain : elle reçoit deux distributions, additionne p ln(p/q) sur les issues où p n'est pas nulle et renvoie l'infini dès qu'une issue possible sous p est impossible sous q. Elle sert de terme de pénalité dans `objectif_rlhf`, de mesure de dérive après PPO et GRPO, et de contrôle de la limite β = 10, où π* reste à moins de 0,01 de π_ref.

**`gabarit_chat(messages)`** — Celle-ci est la mise en page d'une conversation avant l'entraînement, comme un souffleur de théâtre qui surligne dans le texte les seules répliques que l'acteur doit apprendre : elle reçoit une liste de couples rôle et texte, ajoute pour chaque message une balise de rôle de masque 0, puis chaque mot avec le masque 1 s'il vient de l'assistant et 0 sinon, et ajoute après la réponse de l'assistant une balise de fin de masque 1, pour que le modèle apprenne aussi à s'arrêter. Elle renvoie la liste des tokens et celle des masques ; la conversation de `main` donne 13 tokens, dont les cinq derniers, « 50 % du revenu » et la balise de fin, ont un masque de 1.

**`gradient_sft(logits, cibles, masque)`** — Cette fonction dit au modèle comment corriger chaque position de la conversation, mais seulement là où il a quelque chose à apprendre : elle reçoit les logits de chaque position, les indices des tokens cibles et le masque, et renvoie pour chaque position la liste m(p − y)/n, où p est la softmax des logits, y l'indicatrice de la cible et n le nombre de positions de masque 1. Aux positions du prompt, chaque composante vaut exactement 0,0, ce que `main` vérifie avant de comparer la dérivée en une position apprise aux différences finies.

**`perte_bt(r_w, r_l)`** — Celle-ci est le juge du modèle de récompense, qui pénalise toute paire où la réponse préférée ne reçoit pas clairement la meilleure note : elle reçoit les récompenses de la réponse préférée et de la réponse rejetée, et renvoie −ln σ(r_w − r_l), la perte de Bradley-Terry. Pour un écart de 1, elle vaut 0,3133, et la même valeur pour 4 et 3, puisque seule la différence compte ; `main` vérifie aussi que sa dérivée vaut −σ(−1).

**`objectif_rlhf(pi, pi_ref, r, beta)`** — Cette fonction est le tableau de bord du RLHF, qui met en balance la récompense gagnée et la distance prise avec le modèle de référence : elle reçoit une politique, la référence, les récompenses des réponses et β, et renvoie Σ π r − β KL(π ‖ π_ref). Pour la référence elle-même, elle vaut 0,5 × 1 + 0,3 × 2 = 1,1 ; pour la politique optimale, 1,3286, égal à β ln Z ; pour la politique qui met tout sur la meilleure réponse, seulement 0,7960, car la KL la pénalise lourdement.

**`politique_optimale(pi_ref, r, beta)`** — Celle-ci donne la solution exacte du RLHF, comme un notaire qui calcule directement le partage idéal au lieu de le chercher à tâtons : elle reçoit la référence, les récompenses et β, lève une `ValueError` si β n'est pas positif, multiplie chaque probabilité de référence par exp(r/β), puis normalise par la somme Z. Elle renvoie la politique optimale et Z ; pour l'exemple, les poids valent 1,3591, 2,2167 et 0,2, Z vaut 3,7759 et π* vaut 0,3600 ; 0,5871 ; 0,0530, avec une concentration presque totale sur B quand β = 0,1.

**`objectif_ppo(rho, avantage, eps)`** — Cette fonction est le garde-fou de PPO, qui plafonne le bénéfice qu'on peut tirer d'un seul changement de politique : elle reçoit le rapport ρ entre la nouvelle et l'ancienne probabilité d'une réponse, son avantage A et la marge ε, et renvoie le minimum entre ρA et le même produit avec ρ écrêté entre 1 − ε et 1 + ε. Avec A = +2 et ε = 0,2, elle vaut 1,00, 1,60, 2,00, 2,40 et encore 2,40 pour ρ = 0,5, 0,8, 1, 1,2 et 1,5, et `main` vérifie sur 300 valeurs de ρ que le gain par rapport à ρ = 1 ne dépasse jamais ε|A|.

**`derivee_ppo(rho, avantage, eps)`** — Celle-ci est l'interrupteur qui coupe le signal d'apprentissage dès que la borne favorable est franchie : elle reçoit ρ, A et ε, et renvoie A tant que la branche non écrêtée est active, c'est-à-dire quand A est positif et ρ < 1 + ε, ou quand A est négatif et ρ > 1 − ε, et 0 sinon. Elle vaut ainsi 0 pour ρ = 1,5 et A = 2, mais 2 pour ρ = 0,5 et A = 2, parce que la perte reste corrigée du côté défavorable ; `pas_ppo` l'utilise pour freiner la montée.

**`avantages_grpo(recompenses)`** — Cette fonction est l'examinateur qui note chaque copie par rapport à la moyenne de la classe plutôt que dans l'absolu : elle reçoit les récompenses d'un groupe de réponses, lève une `ValueError` si le groupe est vide, calcule leur moyenne et leur écart-type, renvoie une liste de zéros si l'écart-type est nul, sans epsilon caché, et sinon l'écart de chaque récompense à la moyenne divisé par cet écart-type. Pour 1, 0, 0, 1, elle renvoie +1, −1, −1, +1 ; pour un groupe uniforme comme 1, 1, 1, 1, aucun signal, quatre zéros.

**`gradient_kl(z, pi_ref)`** — Celle-ci calcule dans quel sens bouger chaque logit pour se rapprocher de la référence, comme une laisse élastique qui tire d'autant plus fort que le chien s'éloigne : elle reçoit les logits de la politique et la référence, calcule la politique π et sa KL à la référence, et renvoie pour chaque composante πⱼ(ln(πⱼ/π_ref,ⱼ) − KL), le terme +1 de la dérivée de x ln x disparaissant parce que Σᵢ πᵢ(δᵢⱼ − πⱼ) = 0. `pas_grpo` retranche ce gradient multiplié par β à chaque itération.

**`pas_grpo(z, pi_ref, recompense, g, beta, eta, rng)`** — Cette fonction fait une itération complète de GRPO, comme un professeur qui fait plancher un groupe d'élèves sur la même question puis récompense ceux qui dépassent la moyenne : elle reçoit les logits, la référence, la récompense de chaque réponse, la taille g du groupe, β, le pas η et un générateur, tire g réponses selon la politique, calcule leurs avantages par `avantages_grpo`, accumule Σ Aᵢ(e_yᵢ − π)/g, retranche β fois `gradient_kl` et monte d'un pas η. Elle renvoie les nouveaux logits, les tirages et les avantages ; après 30 itérations avec g = 8, β = 0,02, η = 0,5 et la graine 2024, la probabilité de la seule bonne réponse B dépasse 0,9.

**`marge_dpo(z, z_ref, w, l, beta)`** — Celle-ci mesure de combien la politique a creusé l'écart entre la réponse préférée et la réponse rejetée, par rapport à la référence : elle reçoit les logits de la politique et de la référence, les indices de la réponse préférée w et rejetée l, et β, lève une `ValueError` si β n'est pas positif, puis renvoie β fois la différence entre ln π(y_w)/π_ref(y_w) et ln π(y_l)/π_ref(y_l). Elle vaut 0 au départ, quand la politique égale la référence, et c'est elle que `perte_dpo` et `gradient_dpo` transforment en perte et en direction de pas.

**`perte_dpo(z, z_ref, w, l, beta)`** — Cette fonction est la perte de DPO, qui transforme une simple préférence entre deux réponses en signal d'apprentissage, sans modèle de récompense ni génération : elle reçoit les mêmes arguments que `marge_dpo`, calcule la marge et renvoie −ln σ(marge), en laissant remonter la `ValueError` d'un β nul. Partie de la référence, elle vaut ln 2 ≈ 0,6931 ; après un pas de descente avec β = 0,1 et η = 2 sur la préférence de B à A, elle tombe à 0,6832.

**`gradient_dpo(z, z_ref, w, l, beta)`** — Celle-ci est la boussole de DPO, qui pousse la réponse préférée vers le haut et la réponse rejetée vers le bas : elle reçoit les mêmes arguments, calcule la marge h et la politique π, forme les deux gradients e_w − π et e_l − π du logarithme de la probabilité, puis renvoie −β σ(−h) fois leur différence, composante par composante. La composante sur la troisième réponse, ni préférée ni rejetée, vaut exactement 0 ; après un pas, la politique passe de 0,5 ; 0,3 ; 0,2 à 0,4598 ; 0,3370 ; 0,2033.

**`main()`** — C'est le chef de projet qui fait défiler toute la chaîne d'alignement en huit étapes : le SFT masqué sur une conversation de 13 tokens, avec un gradient nul hors masque et vérifié par différences finies, le modèle de récompense de Bradley-Terry, puis la politique optimale du RLHF, son objectif et l'identité J(π) = β ln Z − β KL(π ‖ π*) sur 200 lois tirées au hasard. Viennent ensuite un pas de DPO, trois mille pas qui retrouvent π* à 10⁻⁶ près, l'écrêtage de PPO avec et sans protection, les avantages et 30 pas de GRPO, et enfin trois entrées invalides, groupe vide, β = 0 et masque vide, qui doivent lever `ValueError`.

```python
"""Étape 74 bis — alignement : SFT masqué, Bradley-Terry, RLHF, PPO écrêté, GRPO et DPO sur une politique jouet."""
import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- briques (étape 2)
def softmax(z: list[float]) -> list[float]:
    pic = max(z)
    e = [math.exp(v - pic) for v in z]
    s = sum(e)
    return [v / s for v in e]


def log_softmax(z: list[float]) -> list[float]:
    pic = max(z)
    lse = pic + math.log(sum(math.exp(v - pic) for v in z))
    return [v - lse for v in z]


def sigmoide(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def log_sigmoide(x: float) -> float:
    """ln σ(x), sans débordement : −ln(1 + e^(−x))."""
    return -math.log1p(math.exp(-x)) if x >= 0 else x - math.log1p(math.exp(x))


def kl(p: list[float], q: list[float]) -> float:
    """D_KL(p ‖ q) en nats ; +inf si q(x) = 0 là où p(x) > 0 (étape 50)."""
    total = 0.0
    for pi, qi in zip(p, q):
        if pi > 0:
            if qi == 0:
                return math.inf
            total += pi * math.log(pi / qi)
    return total


# ---------------------------------------------------------------- SFT : gabarit de chat et perte masquée
def gabarit_chat(messages: list[tuple[str, str]]) -> tuple[list[str], list[int]]:
    """Aplatit (rôle, texte) en tokens ; masque = 1 sur le contenu de l'assistant et sa balise de fin."""
    tokens, masque = [], []
    for role, texte in messages:
        tokens.append(f"<{role}>")
        masque.append(0)                                   # la balise de rôle fait partie du prompt
        for mot in texte.split():
            tokens.append(mot)
            masque.append(1 if role == "assistant" else 0)
        if role == "assistant":
            tokens.append("<fin>")
            masque.append(1)                                # le modèle doit apprendre à s'arrêter
    return tokens, masque


def perte_sft(logits: list[list[float]], cibles: list[int], masque: list[int]) -> float:
    """−(1 / Σ m_t) Σ m_t ln π(cible_t) : seules les positions où m_t = 1 comptent."""
    n = sum(masque)
    if n == 0:
        raise ValueError("aucun token à apprendre : le masque est vide")
    return -sum(m * log_softmax(z)[c] for z, c, m in zip(logits, cibles, masque)) / n


def gradient_sft(logits: list[list[float]], cibles: list[int], masque: list[int]) -> list[list[float]]:
    """∂L/∂z_t = m_t (p_t − y_t) / Σ m : exactement nul là où m_t = 0."""
    n = sum(masque)
    grad = []
    for z, c, m in zip(logits, cibles, masque):
        p = softmax(z)
        grad.append([m * (pj - (1.0 if j == c else 0.0)) / n for j, pj in enumerate(p)])
    return grad


# ---------------------------------------------------------------- modèle de récompense (Bradley-Terry)
def perte_bt(r_w: float, r_l: float) -> float:
    """−ln σ(r_w − r_l) : la réponse préférée doit recevoir la plus grande récompense."""
    return -log_sigmoide(r_w - r_l)


# ---------------------------------------------------------------- RLHF : objectif et politique optimale
def objectif_rlhf(pi: list[float], pi_ref: list[float], r: list[float], beta: float) -> float:
    """J(π) = Σ π(y) r(y) − β D_KL(π ‖ π_ref)."""
    return sum(p * ri for p, ri in zip(pi, r)) - beta * kl(pi, pi_ref)


def politique_optimale(pi_ref: list[float], r: list[float], beta: float) -> tuple[list[float], float]:
    """π*(y) = π_ref(y) exp(r(y) / β) / Z."""
    if beta <= 0:
        raise ValueError("il faut beta > 0")
    poids = [q * math.exp(ri / beta) for q, ri in zip(pi_ref, r)]
    z = sum(poids)
    return [w / z for w in poids], z


# ---------------------------------------------------------------- PPO : objectif écrêté
def objectif_ppo(rho: float, avantage: float, eps: float) -> float:
    """min(ρA, clip(ρ, 1 − ε, 1 + ε) A)."""
    return min(rho * avantage, min(max(rho, 1 - eps), 1 + eps) * avantage)


def derivee_ppo(rho: float, avantage: float, eps: float) -> float:
    """dL/dρ : A tant que la branche non écrêtée est active, 0 au-delà de la borne favorable."""
    actif = (avantage > 0 and rho < 1 + eps) or (avantage < 0 and rho > 1 - eps)
    return avantage if actif else 0.0


def pas_ppo(z: list[float], z_old: list[float], y: int, avantage: float, eps: float, eta: float,
            ecretage: bool = True) -> list[float]:
    """Un pas de montée de gradient sur la seule réponse y ; dρ/dz = ρ (e_y − π)."""
    pi = softmax(z)
    rho = pi[y] / softmax(z_old)[y]
    d = derivee_ppo(rho, avantage, eps) if ecretage else avantage
    return [zj + eta * d * rho * ((1.0 if j == y else 0.0) - pj) for j, (zj, pj) in enumerate(zip(z, pi))]


# ---------------------------------------------------------------- GRPO : avantages relatifs au groupe
def avantages_grpo(recompenses: list[float]) -> list[float]:
    """A_i = (r_i − moyenne) / écart-type du groupe ; groupe uniforme : aucun signal, 0 partout."""
    if not recompenses:
        raise ValueError("groupe vide")
    g = len(recompenses)
    moyenne = sum(recompenses) / g
    ecart = math.sqrt(sum((r - moyenne) ** 2 for r in recompenses) / g)
    if ecart == 0.0:
        return [0.0] * g
    return [(r - moyenne) / ecart for r in recompenses]


def gradient_kl(z: list[float], pi_ref: list[float]) -> list[float]:
    """∂ D_KL(π ‖ π_ref) / ∂z_j = π_j (ln(π_j / π_ref,j) − D_KL)."""
    pi = softmax(z)
    d = kl(pi, pi_ref)
    return [pj * (math.log(pj / qj) - d) for pj, qj in zip(pi, pi_ref)]


def pas_grpo(z: list[float], pi_ref: list[float], recompense: list[float], g: int, beta: float, eta: float,
             rng: random.Random) -> tuple[list[float], list[int], list[float]]:
    """Tire g réponses, calcule les avantages, monte le gradient de Σ A_i ln π(y_i) / g − β KL (premier pas : ρ = 1)."""
    pi = softmax(z)
    tirages = rng.choices(range(len(z)), weights=pi, k=g)
    a = avantages_grpo([recompense[y] for y in tirages])
    grad = [0.0] * len(z)
    for y, ai in zip(tirages, a):
        for j in range(len(z)):
            grad[j] += ai * ((1.0 if j == y else 0.0) - pi[j]) / g
    gkl = gradient_kl(z, pi_ref)
    return [zj + eta * (gj - beta * kj) for zj, gj, kj in zip(z, grad, gkl)], tirages, a


# ---------------------------------------------------------------- DPO
def marge_dpo(z: list[float], z_ref: list[float], w: int, l: int, beta: float) -> float:
    """h = β [ln π(y_w)/π_ref(y_w) − ln π(y_l)/π_ref(y_l)]."""
    if beta <= 0:
        raise ValueError("il faut beta > 0")
    lp, lr = log_softmax(z), log_softmax(z_ref)
    return beta * ((lp[w] - lr[w]) - (lp[l] - lr[l]))


def perte_dpo(z: list[float], z_ref: list[float], w: int, l: int, beta: float) -> float:
    return -log_sigmoide(marge_dpo(z, z_ref, w, l, beta))


def gradient_dpo(z: list[float], z_ref: list[float], w: int, l: int, beta: float) -> list[float]:
    """−β σ(−h) [∇ ln π(y_w) − ∇ ln π(y_l)], avec ∇_z ln π(y) = e_y − π (étape 2)."""
    h = marge_dpo(z, z_ref, w, l, beta)
    pi = softmax(z)
    grad_w = [(1.0 if j == w else 0.0) - pj for j, pj in enumerate(pi)]
    grad_l = [(1.0 if j == l else 0.0) - pj for j, pj in enumerate(pi)]
    return [-beta * sigmoide(-h) * (a - b) for a, b in zip(grad_w, grad_l)]


def main() -> None:
    print("1. SFT : gabarit de chat et perte masquée")
    tokens, masque = gabarit_chat([("system", "agent crédit"), ("user", "plafond d'endettement ?"),
                                   ("assistant", "50 % du revenu")])
    vocab = sorted(set(tokens))
    entrees, cibles, m = tokens[:-1], [vocab.index(t) for t in tokens[1:]], masque[1:]
    rng = random.Random(74)
    logits = [[rng.uniform(-1, 1) for _ in vocab] for _ in entrees]
    print("  appris : " + " ".join(t for t, mt in zip(tokens[1:], m) if mt))
    l_masque = perte_sft(logits, cibles, m)
    l_tout = perte_sft(logits, cibles, [1] * len(cibles))
    print(f"  perte masquée {l_masque:.4f} sur {sum(m)} tokens ; sans masque {l_tout:.4f} sur {len(cibles)} tokens")
    assert sum(m) == 5 and [t for t, mt in zip(tokens[1:], m) if mt] == ["50", "%", "du", "revenu", "<fin>"]
    grad = gradient_sft(logits, cibles, m)
    assert all(g == 0.0 for gz, mt in zip(grad, m) if mt == 0 for g in gz)          # gradient nul hors masque
    perturbe = [list(z) for z in logits]
    perturbe[4] = [v + 5.0 * (k % 2) for k, v in enumerate(perturbe[4])]           # entrée « plafond », message utilisateur
    assert entrees[4] == "plafond" and m[4] == 0 and perte_sft(perturbe, cibles, m) == l_masque
    i = m.index(1)
    dz = 1e-6
    plus = [list(z) for z in logits]
    plus[i][0] += dz
    assert abs((perte_sft(plus, cibles, m) - l_masque) / dz - grad[i][0]) < 1e-5    # différences finies

    print("2. Modèle de récompense : Bradley-Terry")
    print(f"  r_w - r_l = 1 : P(préférée) = {sigmoide(1.0):.4f}, perte = {perte_bt(1.0, 0.0):.4f}")
    assert round(sigmoide(1.0), 4) == 0.7311 and round(perte_bt(1.0, 0.0), 4) == 0.3133
    assert abs(perte_bt(4.0, 3.0) - perte_bt(1.0, 0.0)) < 1e-12                      # seule la différence compte
    d_num = (perte_bt(1.0 + 1e-6, 0.0) - perte_bt(1.0, 0.0)) / 1e-6
    assert abs(d_num + sigmoide(-1.0)) < 1e-5                                         # dérivée −σ(−d)

    print("3. RLHF : la politique optimale est π_ref·exp(r/β)/Z")
    pi_ref, r, beta = [0.5, 0.3, 0.2], [1.0, 2.0, 0.0], 1.0
    pi_opt, z_part = politique_optimale(pi_ref, r, beta)
    print("  π* = (" + ", ".join(f"{p:.4f}" for p in pi_opt) + f") ; Z = {z_part:.4f}")
    j_opt, j_ref = objectif_rlhf(pi_opt, pi_ref, r, beta), objectif_rlhf(pi_ref, pi_ref, r, beta)
    j_glouton = objectif_rlhf([0.0, 1.0, 0.0], pi_ref, r, beta)
    print(f"  J(π*) = {j_opt:.4f} = β ln Z ; J(π_ref) = {j_ref:.4f} ; J(tout sur la meilleure) = {j_glouton:.4f}")
    assert abs(j_opt - beta * math.log(z_part)) < 1e-12 and j_opt > j_ref > j_glouton
    rng_d = random.Random(740)
    for _ in range(200):
        w = [rng_d.random() for _ in range(3)]
        pi = [x / sum(w) for x in w]
        assert abs(objectif_rlhf(pi, pi_ref, r, beta) - (beta * math.log(z_part) - beta * kl(pi, pi_opt))) < 1e-12
    r_impl = [beta * math.log(p / q) for p, q in zip(pi_opt, pi_ref)]
    assert all(abs((r_impl[i] - r_impl[j]) - (r[i] - r[j])) < 1e-12 for i in range(3) for j in range(3))
    for b in (0.1, 10.0):
        print(f"  β = {b:>4} : π* = (" + ", ".join(f"{p:.4f}" for p in politique_optimale(pi_ref, r, b)[0]) + ")")
    assert politique_optimale(pi_ref, r, 0.1)[0][1] > 0.99 and kl(politique_optimale(pi_ref, r, 10.0)[0], pi_ref) < 0.01

    print("4. DPO : un pas sur une préférence (B préférée à A, β = 0.1, η = 2)")
    z_ref = [math.log(p) for p in pi_ref]
    z = list(z_ref)
    w_, l_ = 1, 0
    avant = softmax(z)
    perte_avant = perte_dpo(z, z_ref, w_, l_, 0.1)
    g = gradient_dpo(z, z_ref, w_, l_, 0.1)
    z = [zj - 2.0 * gj for zj, gj in zip(z, g)]
    apres = softmax(z)
    print("  π avant (" + ", ".join(f"{p:.4f}" for p in avant) + ") -> après (" + ", ".join(f"{p:.4f}" for p in apres) + ")")
    print(f"  perte {perte_avant:.4f} -> {perte_dpo(z, z_ref, w_, l_, 0.1):.4f} ; gradient sur C = {abs(g[2]):.1f}")
    assert apres[w_] > avant[w_] and apres[l_] < avant[l_] and g[2] == 0.0
    assert abs(perte_avant - math.log(2)) < 1e-12 and perte_dpo(z, z_ref, w_, l_, 0.1) < perte_avant
    assert (round(apres[0], 4), round(apres[1], 4), round(apres[2], 4)) == (0.4598, 0.3370, 0.2033)

    print("5. DPO converge vers π* sans modèle de récompense ni RL")
    r_vrai, beta_dpo = [0.0, 1.0, -1.0], 0.5
    cible = politique_optimale(pi_ref, r_vrai, beta_dpo)[0]
    u = [0.0, 0.0, 0.0]                                  # u = z − z_ref, la politique part de π_ref
    for _ in range(3000):
        grad_u = [0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(3):
                if i != j:
                    q = sigmoide(r_vrai[i] - r_vrai[j])  # P(i préférée à j) selon Bradley-Terry
                    grad_u[i] += beta_dpo * (sigmoide(beta_dpo * (u[i] - u[j])) - q)
        u = [ui - 1.0 * gi for ui, gi in zip(u, grad_u)]
    pi_dpo = softmax([a + b for a, b in zip(z_ref, u)])
    print("  π_DPO = (" + ", ".join(f"{p:.4f}" for p in pi_dpo) + ") ; π* = (" + ", ".join(f"{p:.4f}" for p in cible) + ")")
    assert max(abs(a - b) for a, b in zip(pi_dpo, cible)) < 1e-6

    print("6. PPO : l'écrêtage borne le gain (ε = 0.2)")
    for a_ in (2.0, -2.0):
        valeurs = [objectif_ppo(rho, a_, 0.2) for rho in (0.5, 0.8, 1.0, 1.2, 1.5)]
        print(f"  A = {a_:+.0f} : ρ = 0.5, 0.8, 1, 1.2, 1.5 -> " + "  ".join(f"{v:+.2f}" for v in valeurs))
        for k in range(1, 301):
            rho = k / 100
            assert objectif_ppo(rho, a_, 0.2) - objectif_ppo(1.0, a_, 0.2) <= 0.2 * abs(a_) + 1e-12
    assert derivee_ppo(1.5, 2.0, 0.2) == 0.0 and derivee_ppo(0.5, -2.0, 0.2) == 0.0
    assert derivee_ppo(0.5, 2.0, 0.2) == 2.0 and derivee_ppo(1.5, -2.0, 0.2) == -2.0   # la perte reste corrigée
    z_old = [math.log(p) for p in pi_ref]
    rhos = {}
    for eta_ppo in (0.05, 0.5):
        for ecretage in (True, False):
            z = list(z_old)
            for _ in range(60):
                z = pas_ppo(z, z_old, 2, 1.0, 0.2, eta_ppo, ecretage)
            rhos[(eta_ppo, ecretage)] = (softmax(z)[2] / 0.2, kl(softmax(z), pi_ref))
        print(f"  η = {eta_ppo:<4}, 60 pas sur la réponse C (A = +1) : ρ = {rhos[(eta_ppo, True)][0]:.3f} avec écrêtage"
              f" (KL {rhos[(eta_ppo, True)][1]:.4f}), {rhos[(eta_ppo, False)][0]:.3f} sans (KL {rhos[(eta_ppo, False)][1]:.4f})")
    assert 1.2 <= rhos[(0.05, True)][0] < 1.26 and rhos[(0.05, False)][0] > 3.0
    assert rhos[(0.5, True)][0] > 1.5                    # un pas trop long saute la borne : ρ n'est pas borné

    print("7. GRPO : avantages relatifs au groupe, sans réseau de valeur")
    for groupe in ([1, 0, 0, 1], [1, 0, 0, 0], [1, 1, 1, 1]):
        a = avantages_grpo(groupe)
        print(f"  récompenses {groupe} -> avantages [" + ", ".join(f"{x:+.4f}" for x in a) + "]")
        if any(a):
            assert abs(sum(a)) < 1e-12 and abs(sum(x * x for x in a) / len(a) - 1) < 1e-12
    assert avantages_grpo([1, 1, 1, 1]) == [0.0, 0.0, 0.0, 0.0]
    for p_, g_ in ((0.95, 8), (0.5, 8)):
        print(f"  p = {p_}, G = {g_} : P(groupe uniforme, gradient nul) = {p_ ** g_ + (1 - p_) ** g_:.4f}")
    pi_test = softmax([0.3, -1.2, 0.8])
    for j in range(3):
        assert abs(sum(pi_test[y] * ((1.0 if j == y else 0.0) - pi_test[j]) for y in range(3))) < 1e-15   # E[∇ ln π] = 0
    rng_g = random.Random(2024)
    z = [math.log(p) for p in pi_ref]
    recompense = [0.0, 1.0, 0.0]                         # seule la réponse B passe le test
    for _ in range(30):
        z, _, _ = pas_grpo(z, pi_ref, recompense, 8, 0.02, 0.5, rng_g)
    pi_final = softmax(z)
    print(f"  30 pas, G = 8 : π(B) = {pi_ref[1]:.4f} -> {pi_final[1]:.4f} ; KL(π ‖ π_ref) = {kl(pi_final, pi_ref):.4f}")
    assert pi_final[1] > 0.9

    for appel in (lambda: avantages_grpo([]), lambda: perte_dpo([0.0], [0.0], 0, 0, 0.0),
                  lambda: perte_sft([[0.0]], [0], [0])):
        try:
            appel()
        except ValueError:
            pass
        else:
            raise AssertionError("une entrée invalide aurait dû être refusée")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
…
3. RLHF : la politique optimale est π_ref·exp(r/β)/Z
  π* = (0.3600, 0.5871, 0.0530) ; Z = 3.7759
  J(π*) = 1.3286 = β ln Z ; J(π_ref) = 1.1000 ; J(tout sur la meilleure) = 0.7960
  β =  0.1 : π* = (0.0001, 0.9999, 0.0000)
  β = 10.0 : π* = (0.4938, 0.3275, 0.1787)
4. DPO : un pas sur une préférence (B préférée à A, β = 0.1, η = 2)
  π avant (0.5000, 0.3000, 0.2000) -> après (0.4598, 0.3370, 0.2033)
  perte 0.6931 -> 0.6832 ; gradient sur C = 0.0
5. DPO converge vers π* sans modèle de récompense ni RL
  π_DPO = (0.1822, 0.8079, 0.0099) ; π* = (0.1822, 0.8079, 0.0099)
6. PPO : l'écrêtage borne le gain (ε = 0.2)
  A = +2 : ρ = 0.5, 0.8, 1, 1.2, 1.5 -> +1.00  +1.60  +2.00  +2.40  +2.40
  A = -2 : ρ = 0.5, 0.8, 1, 1.2, 1.5 -> -1.60  -1.60  -2.00  -2.40  -3.00
  η = 0.05, 60 pas sur la réponse C (A = +1) : ρ = 1.223 avec écrêtage (KL 0.0060), 4.599 sans (KL 1.2206)
  η = 0.5 , 60 pas sur la réponse C (A = +1) : ρ = 1.577 avec écrêtage (KL 0.0378), 4.977 sans (KL 1.5736)
…
OK — toutes les vérifications sont passées.
```

Le programme montre quatre choses. Le masque SFT annule exactement le gradient hors de la réponse. L'objectif du RLHF a une solution fermée, π_ref · exp(r/β)/Z, et DPO l'atteint sans modèle de récompense ni génération. L'écrêtage de PPO borne le gain de l'objectif, mais pas le rapport ρ quand le pas est trop long. Enfin, GRPO tire son signal de l'écart entre réponses d'un même groupe, et n'en reçoit aucun quand le groupe est uniforme.

### Passer à un vrai modèle sans dépendre d'un framework

Sur un vrai LLM, la seule pièce nouvelle est la log-probabilité d'une réponse entière : la somme des log-probabilités de ses tokens, avec le même masque que le SFT. Les pertes, elles, tiennent en quelques lignes, quel que soit l'outil de calcul tensoriel. Des bibliothèques du marché, comme TRL de Hugging Face (SFTTrainer, DPOTrainer, GRPOTrainer), les emballent avec la gestion des lots et de la mémoire. Elles restent un confort, pas un prérequis : tout ce qu'elles calculent est dans ce fichier.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`logprob_reponse(logits, cibles, masque)`** — Cette fonction est la seule pièce nouvelle sur un vrai modèle, le greffier qui additionne la vraisemblance de chaque mot d'une réponse entière : elle reçoit un tenseur de logits de forme lot × positions × vocabulaire, les tokens cibles et le masque, de forme lot × positions, calcule le log-softmax sur le vocabulaire, en extrait par `gather` la log-probabilité du token cible à chaque position, la multiplie par le masque pour ne garder que la réponse, puis somme le long des positions. Elle renvoie, pour chaque exemple du lot, ln π(y | x), avec le même masque que le SFT du programme précédent.

**`perte_dpo(lp_w, lp_l, lp_ref_w, lp_ref_l, beta)`** — C'est la même perte DPO que dans le programme précédent, mais écrite sur des lots de log-probabilités de réponses entières plutôt que sur une politique jouet à trois réponses : elle reçoit les log-probabilités des réponses préférées et rejetées sous la politique et sous la référence, ainsi que β = 0,1 par défaut, calcule la marge β((lp_w − lp_ref_w) − (lp_l − lp_ref_l)) et renvoie la moyenne sur le lot de −ln σ(marge), grâce à `F.logsigmoid`. Contrairement à la version en Python pur, elle ne refuse pas un β nul, et le commentaire rappelle que les log-probabilités de référence se calculent hors du graphe de gradient.

```python
# [extrait] — perte DPO en PyTorch (non exécuté : PyTorch n'est pas dans la bibliothèque standard)
import torch
import torch.nn.functional as F


def logprob_reponse(logits: torch.Tensor, cibles: torch.Tensor, masque: torch.Tensor) -> torch.Tensor:
    """logits (lot, T, |V|) ; cibles et masque (lot, T) ; masque = 1 sur les tokens de la réponse."""
    lp = F.log_softmax(logits, dim=-1).gather(-1, cibles.unsqueeze(-1)).squeeze(-1)
    return (lp * masque).sum(dim=-1)                        # ln π(y | x), sur la seule réponse


def perte_dpo(lp_w, lp_l, lp_ref_w, lp_ref_l, beta: float = 0.1) -> torch.Tensor:
    marge = beta * ((lp_w - lp_ref_w) - (lp_l - lp_ref_l))  # les lp_ref sont calculés sous torch.no_grad()
    return -F.logsigmoid(marge).mean()
```

## Squelette algorithmique

Le fichier présente trois algorithmes d'entraînement :

- **le SFT masqué**, qui apprend les réponses de l'assistant ;
- **DPO**, qui apprend à partir de paires de préférences ;
- **une itération de GRPO**, qui apprend à partir d'une récompense calculée sur des réponses générées. Une itération de PPO a la même forme, avec un critique à la place de la moyenne du groupe.

Les trois tournent hors ligne, avant le déploiement.

### SFT masqué

Entrées : des conversations modèles, avec leur gabarit de chat. Sortie : les paramètres ajustés.

```text
ALGORITHME SFTMasqué
ENTRÉES : conversations (rôle, texte), gabarit de chat, paramètres θ, pas η
SORTIE  : θ ajusté

  POUR CHAQUE conversation FAIRE
      (tokens, masque) ← gabarit(conversation)          (1 sur la réponse et sa balise de fin)
      cibles ← tokens décalés d'un rang ; masque décalé de même
      perte ← − Σ masque[t] × ln π(cibles[t]) / Σ masque
      SI Σ masque = 0 ALORS ERREUR « rien à apprendre »
      θ ← θ − η × gradient(perte)                       (nul sur les positions masquées)
  FIN POUR
  RETOURNER θ
```

**Complexité :** O(n × |V|) par conversation pour les softmax de la perte, où n est la longueur et |V| la taille du vocabulaire. Dans un vrai modèle, le coût est dominé par les passes avant et arrière du réseau, proportionnelles à n. La mémoire vaut O(n × |V|) pour les logits d'une séquence.

**Du squelette au code :** `gabarit_chat` produit les tokens et le masque, le décalage est la ligne `cibles = tokens[1:]` et `masque[1:]` de `main`, la perte est `perte_sft`, et le gradient est `gradient_sft`.

### DPO

Entrées : des paires de préférences, une politique de départ (en général le modèle après SFT) et une référence gelée. Sortie : la politique entraînée.

```text
ALGORITHME DPO
ENTRÉES : paires (x, y_w, y_l), politique θ (au départ = référence), référence gelée, β, pas η
SORTIE  : θ entraîné

  POUR CHAQUE paire FAIRE (une seule fois)
      lp_ref_w ← ln π_ref(y_w | x) ; lp_ref_l ← ln π_ref(y_l | x)      (précalculables)
  FIN POUR
  POUR CHAQUE époque, POUR CHAQUE paire FAIRE
      h ← β × [(ln π_θ(y_w | x) − lp_ref_w) − (ln π_θ(y_l | x) − lp_ref_l)]
      perte ← − ln σ(h)
      θ ← θ − η × gradient(perte)                       (poids σ(−h) : grand si la paire est mal classée)
  FIN POUR
  RETOURNER θ
```

**Complexité :** par paire et par époque, deux calculs de log-probabilité de réponse avec leur gradient, sur la politique. Les deux calculs de la référence ne se font qu'une fois. Il n'y a aucune génération pendant l'entraînement. La mémoire contient une seule copie entraînée, plus la référence si l'on ne précalcule pas ses log-probabilités.

**Du squelette au code :** h est `marge_dpo`, la perte est `perte_dpo` et le gradient est `gradient_dpo`. Le pas de mise à jour est la ligne `z = [zj - 2.0 * gj ...]` du bloc 4 de `main`, et la boucle sur toutes les paires est le bloc 5.

### Une itération de GRPO

Entrées : des questions munies d'une fonction de récompense, la politique, la référence et les réglages G, ε, β, η. Sortie : la politique mise à jour.

```text
ALGORITHME ItérationGRPO
ENTRÉES : questions, fonction de récompense R, politique θ, référence, taille de groupe G, ε, β, pas η
SORTIE  : θ mis à jour

  POUR CHAQUE question x FAIRE
      π_old ← copie gelée de π_θ
      tirer G réponses y₁ … y_G selon π_old(· | x)
      rᵢ ← R(x, yᵢ) pour chaque i
      SI toutes les rᵢ sont égales ALORS passer à la question suivante      (aucun signal)
      Aᵢ ← (rᵢ − moyenne) / écart-type
      POUR CHAQUE passe sur le lot FAIRE
          ρᵢ ← π_θ(yᵢ | x) / π_old(yᵢ | x)
          objectif ← moyenne de min(ρᵢ Aᵢ, clip(ρᵢ, 1 − ε, 1 + ε) Aᵢ) − β × KL(π_θ ‖ référence)
          θ ← θ + η × gradient(objectif)
          SI KL(π_θ ‖ π_old) > seuil ALORS arrêter les passes
      FIN POUR
  FIN POUR
  RETOURNER θ
```

**Complexité :** par question, G générations, dont le coût croît linéairement avec G (étape 72 quinquies, point 7), puis G calculs de log-probabilité avec gradient à chaque passe. La mémoire contient la politique, la référence et la fonction de récompense. Celle-ci n'est pas un réseau quand elle est vérifiable ; il n'y a pas de critique.

**Du squelette au code :** les avantages sont `avantages_grpo`, et le cas « toutes égales » est sa branche `ecart == 0.0`. L'objectif écrêté et sa dérivée sont `objectif_ppo` et `derivee_ppo`, le pas complet (tirage, avantages, gradient, KL) est `pas_grpo`, et le gradient de la KL est `gradient_kl`. Le seuil de KL qui arrête les passes est la parade à la nuance du point 7, illustrée dans le bloc 6 de `main`.

## Cas d'usage réels aux Émirats

Les volumes, taux et réglages ci-dessous sont illustratifs. Les règles citées sont à confirmer avec le texte en vigueur.

### Banque — un extracteur KYC ajusté sans apprendre à réécrire les clients

Une banque de détail de Dubaï ajuste, avec LoRA (étape 73), un petit modèle ouvert. Il doit transformer une conversation d'ouverture de compte en un JSON KYC strict : nom, Emirates ID (format à 15 chiffres commençant par 784), employeur, revenu. Le jeu d'entraînement compte 3 000 conversations validées par la conformité.

Le gabarit de chat place le prompt système, les messages du client et la réponse attendue, et la perte SFT est masquée. Seuls le JSON de l'assistant et sa balise de fin comptent : dans l'exemple du code, 5 positions sur 12.

Sans masque, le modèle apprendrait aussi à prédire les messages des clients. Il dépenserait sa capacité à les imiter, et surtout il pourrait en restituer des fragments en générant : des numéros, des salaires. Avec le masque, le texte du client sert de contexte, mais il n'est jamais une cible. La banque n'en conclut pas qu'elle peut se passer d'anonymisation : le point 1 montre que ce texte influence encore le gradient à travers l'attention. Les données sont donc pseudonymisées avant l'entraînement, conformément à sa politique de protection des données.

On suit deux indicateurs : le taux de JSON conformes au schéma sur un jeu de test (étape 11), et le taux de sorties contenant un identifiant absent de l'entrée, dont l'objectif est zéro.

### Assurance — DPO à partir des corrections des gestionnaires

Un assureur auto et santé fait rédiger par un agent les courriers de décision sur les sinistres, et les gestionnaires corrigent les brouillons avant envoi. Chaque correction fournit une paire : le brouillon est la réponse rejetée, la version corrigée la réponse préférée.

Avec 4 000 paires, l'équipe applique DPO avec β = 0,1, sans modèle de récompense ni apprentissage par renforcement. Elle garde deux modèles, et elle calcule une fois pour toutes les log-probabilités de la référence.

Le point 5 dit comment lire l'entraînement. Le poids σ(−h) concentre l'effort sur les paires que le modèle classe encore mal. L'indicateur naturel est donc la part des paires de validation où la marge h est positive.

Toutes les corrections ne se valent pas : une faute de frappe corrigée n'apprend pas la même chose qu'une décision de couverture changée. L'équipe filtre donc les paires, et la décision de couverture elle-même reste produite par une règle et validée par un humain. DPO n'apprend que la rédaction. L'assurance est supervisée par la CBUAE, et un courrier qui contredit la police est un risque de réclamation. L'indicateur suivi en production est le taux de courriers corrigés par les gestionnaires, mois après mois.

### RH — GRPO avec une récompense vérifiable

Un cabinet RH présent dans plusieurs émirats veut que son modèle appelle l'outil `gratuite_fin_de_service` du code canonique avec les bons arguments : salaire de base, ancienneté, type de cas. Il doit les extraire d'un message de salarié, en arabe ou en anglais.

La récompense est vérifiable : elle vaut 1 si le montant calculé avec les arguments du modèle est exactement celui de la référence (correspondance exacte, étape 64), et 0 sinon. Il n'y a donc pas de modèle de récompense à entraîner.

GRPO tire G = 8 réponses par question. Le point 8 impose une sélection des questions : sur les questions simples, où le modèle réussit déjà avec p = 0,95, deux groupes sur trois sont uniformes et n'apprennent rien. L'équipe mesure donc p par question avec le modèle courant et garde celles où p est compris entre 0,2 et 0,8.

La pénalité de KL, avec β = 0,02, empêche le modèle de dériver sur ce qu'il savait déjà faire, comme répondre poliment dans les deux langues. Les règles du décret-loi fédéral 33/2021 restent dans l'outil, pas dans les poids : le modèle apprend à extraire des arguments, pas le droit du travail. Les salariés du DIFC, qui relèvent du régime DEWS, figurent dans les données comme un cas de renvoi récompensé. On suit la correspondance exacte sur un jeu de test, la KL par rapport à la référence et la part de groupes uniformes.

### Crypto — un modèle de récompense qui préfère les résumés longs

Une plateforme d'actifs virtuels agréée par la VARA fait rédiger par un agent les résumés d'incidents de liquidité destinés aux rapports de conformité. Des analystes comparent des paires de résumés, et l'équipe entraîne un modèle de récompense de Bradley-Terry (point 2, et étape 65 bis).

Après la phase de RL, les résumés s'allongent de version en version. L'enquête montre que les analystes préféraient légèrement les résumés plus détaillés : le modèle de récompense a appris « plus long vaut mieux ». La politique exploite ce raccourci, ce qui illustre la loi de Goodhart : une mesure qui devient un objectif cesse d'être une bonne mesure.

Le point 2 explique pourquoi rien, dans la perte, ne protège contre ce raccourci : elle ne voit que des différences de note. L'équipe adopte trois parades :

- elle compare désormais des paires de longueurs proches ;
- elle relève β, pour rapprocher la politique de sa référence (point 3) ;
- elle suit la longueur moyenne des résumés à chaque version.

Un rapport de conformité trop long n'est pas un rapport meilleur. Il est lu plus tard, et une alerte importante peut s'y perdre. L'indicateur suivi est le taux de victoire du nouveau modèle dans des comparaisons à l'aveugle, à longueur comparable.

### BTP — choisir la méthode selon la mémoire disponible

Un groupe de construction à Dubaï veut aligner un modèle ouvert de 7 milliards de paramètres pour rédiger ses comptes rendus de chantier. Les données restent sur ses propres serveurs. En FP16, à 2 octets par paramètre, une copie des poids occupe 7 × 10⁹ × 2 = 14 Go.

La méthode détermine le nombre de copies à garder en mémoire :

| Méthode | Modèles en mémoire | Poids seuls (Go) |
|---|---|---|
| PPO | politique, référence, récompense, critique | 56 |
| GRPO | politique, référence (récompense vérifiable) | 28 |
| DPO | politique (référence précalculée) | 14 |

PPO entraîne en plus deux de ces réseaux, ce qui ajoute les deux moments d'Adam pour chacun de leurs paramètres (étape 74). Sur un serveur de 48 Go, le RLHF par PPO ne tient pas sans découpage du modèle, alors que DPO avec LoRA tient largement. Le groupe dispose de comptes rendus validés et de versions corrigées par les conducteurs de travaux : il a des paires, pas de récompense calculable. Il choisit donc un SFT puis DPO. L'indicateur suivi est le taux de victoire face au modèle SFT seul, avec le coût de chaque entraînement.

### Secteur public — garder l'arabe en alignant sur l'anglais

Une entité de services publics en ligne, accessible par UAE Pass, répond en arabe et en anglais. Elle part d'un modèle ouvert bilingue (Jais ou Falcon sont des exemples du marché) et l'aligne par DPO sur des paires de préférences, dont 80 % sont en anglais.

Avec un β de 0,02, les réponses en anglais progressent, mais les réponses en arabe se dégradent : registre moins soutenu, mots anglais glissés dans la phrase. La KL mesurée séparément par langue le confirme : elle monte bien plus vite sur les questions en arabe, où les préférences sont rares.

Le point 3 donne le levier : β contrôle la distance à la référence, qui porte la compétence en arabe. L'équipe relève β à 0,1, ajoute des paires en arabe et évalue chaque langue séparément. Les paires contiennent des questions d'usagers : elles sont pseudonymisées, et le cadre légal applicable à une entité publique est à confirmer avec le texte en vigueur. On suit le taux de victoire par langue, la KL par langue et la régularité du registre en arabe.

## Pièges et limites

- **Décaler le masque d'un rang.** Si le masque est aligné sur les entrées et non sur les cibles, le modèle apprend à prédire la balise `<assistant>` et jamais la balise de fin : il ne s'arrête plus. Le code aligne `masque[1:]` sur `cibles = tokens[1:]`.
- **Faire confiance au modèle de récompense.** Il apprend aussi les biais des annotateurs (longueur, ton assuré). La politique les exploite, d'autant plus que β est petit. On évalue toujours à l'aveugle, sur des humains ou sur une récompense vérifiable.
- **Croire que DPO fait toujours monter la réponse préférée.** Pour un vrai LLM, DPO ne contraint que la marge h. Les log-probabilités de la préférée et de la rejetée peuvent baisser ensemble, la masse partant vers des réponses qui ne figurent dans aucune paire. Le point 5 en montre l'amorce : la troisième réponse monte. On surveille ln π(y_w) pendant l'entraînement.
- **Prendre l'écrêtage de PPO pour une borne sur ρ.** Il borne l'incitation, pas le déplacement (point 7). On surveille la KL entre π_θ et π_old, on arrête les passes au-delà d'un seuil, et l'on garde des pas petits.
- **Entraîner GRPO sur des questions trop faciles ou trop difficiles.** Les groupes uniformes ne donnent aucun gradient. Pire, un groupe presque uniforme a un petit écart-type, et la division par cet écart-type amplifie son bruit. On sélectionne les questions selon leur p mesuré.

### Exercice feuille blanche

1. Sans regarder le code, écrire `perte_dpo` et `gradient_dpo` à partir des formules. Vérifier qu'un pas fait monter π(y_w) et que la composante du gradient sur la troisième réponse est nulle.
2. Prédire, puis vérifier : que devient π* quand β → 0, puis quand β → ∞ ? Calculer π* pour π_ref = (0,5 ; 0,5), r = (0 ; 1) et β = 1. (Réponse : la meilleure réponse seule, puis π_ref ; ensuite π* = (1/(1 + e) ; e/(1 + e)) = (0,2689 ; 0,7311).)
3. Trouver le bug : un collègue écrit `max` au lieu du premier `min` dans `objectif_ppo`. Que renvoie sa version pour ρ = 1,5 et A = +2, et pour ρ = 0,5 et A = +2 ? (Réponse : 3,0 au lieu de 2,4, donc un gain qui n'est plus borné ; puis 1,6 au lieu de 1,0, avec une dérivée nulle, donc un mauvais mouvement qui n'est plus corrigé.)

## Pour aller plus loin

- **Les articles fondateurs.** La chaîne SFT, modèle de récompense, PPO a été popularisée par InstructGPT (Ouyang et al., 2022), et PPO vient de Schulman et al. (2017). DPO est dû à Rafailov et al. (2023), GRPO à Shao et al. (2024, DeepSeekMath).
- **Les variantes de DPO.** IPO, KTO, ORPO et SimPO changent la perte : KTO, par exemple, se contente d'étiquettes « bonne » ou « mauvaise », sans paires.
- **Les variantes de GRPO.** RLOO exclut la réponse i de sa propre moyenne (point 8). Plusieurs travaux proposent aussi de ne pas diviser par l'écart-type.
- **L'estimation de la KL.** GRPO estime la KL token par token avec un estimateur toujours positif, π_ref/π − ln(π_ref/π) − 1, plutôt que par ln(π/π_ref).
- **Les retours d'IA.** Le RLAIF, ou l'approche « constitutionnelle », remplace les annotateurs humains par un modèle juge guidé par des principes écrits. On retrouve les limites du juge imparfait de l'étape 72 quinquies.
- **Les agents à plusieurs étapes.** Pour un agent qui enchaîne des actions, l'avantage se calcule sur toute la trajectoire, avec un facteur d'actualisation et une estimation lissée (GAE). C'est le lien avec le MDP et l'équation de Bellman de l'étape 38.

> Étape 74 bis du parcours · Prérequis : [Optimiseur Adam](<74-Optimiseur-Adam.md>) · Suite : [Optimisation : formules manquantes](<75-Optimisation-Formules.md>)
