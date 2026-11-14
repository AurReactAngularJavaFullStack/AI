# Étape 78 — Les mathématiques de l'IA agentique
## Comprendre, décider, mesurer, fiabiliser

### 01  Objectif : construire des agents utiles et maitrisés

**Support technique pour Aurélien  Architecture IA, Java, Angular et SaaS**

Un agent ne se contente pas de produire du texte : il choisit des actions, consulte des sources, utilise des outils et modifie parfois un système réel. Ses erreurs peuvent donc se cumuler, couter de l'argent ou provoquer des effets irréversibles.

Les mathématiques servent ici à répondre à quatre questions :

1. **Comprendre** : comment les modèles représentent-ils et sélectionnent-ils l'information ?
2. **Décider** : quelle action apporte une valeur suffisante pour justifier son cout ?
3. **Mesurer** : une amélioration observée est-elle réelle et reproductible ?
4. **Fiabiliser** : comment limiter les erreurs, les délais et les risques ?

**Aucune liste de formules n'est exhaustive.** Devenir excellent développeur d'agents ne suppose pas de réentrainer un grand modèle de langage. La priorité est de maitriser les probabilités, l'évaluation, la recherche d'information et les systèmes distribués.

Ce document est un **support Markdown structuré en diapositives**, indépendant d'un logiciel de présentation.

---

## 02  Carte des priorités : production avant sophistication

Les notions n'ont pas toutes le même rendement professionnel.

| Niveau                 | À maîtriser                                                  | Utilité principale                             |
| ---------------------- | ------------------------------------------------------------ | ---------------------------------------------- |
| **P0  Indispensable**  | Probabilités, couts, contexte cumulé d'une boucle, similarité, métriques RAG, fiabilité, pass^k, statistiques d'évaluation, juge LLM, sécurité | Construire et exploiter un agent               |
| **P1  Optimisation**   | Attention, théorie de l'information, mémoire, décision séquentielle, files d'attente, calibration, bandits | Comprendre les limites et améliorer le système |
| **P2  Spécialisation** | Gradients, divergences, apprentissage par renforcement       | Adapter ou entrainer des modèles               |

Ces niveaux indiquent un **ordre d'apprentissage**, pas une frontière absolue. Par exemple, la calibration devient indispensable si un score déclenche automatiquement une transaction.

**Parcours conseillé :**

- Commencer par un agent simple et un jeu d'évaluation représentatif.
- Mesurer réussite, cout, latence et incidents.
- Identifier le principal facteur limitant.
- Étudier ensuite les mathématiques nécessaires à son amélioration.

**Piège :** optimiser la sophistication du raisonnement avant de vérifier les permissions, les données et les outils. Un agent mal autorisé reste dangereux, même avec un excellent modèle.

---

## 03  Notation commune : état, historique, action et politique

À l'instant t, distinguons :

- sₜ : état réel de l'environnement, souvent partiellement caché ;
- oₜ : observation reçue ;
- hₜ : historique disponible ;
- aₜ : action choisie ;
- π : politique de décision.

$$
h_t=(o_0,a_0,o_1,a_1,\ldots,o_t)
$$

$$
a_t\sim\pi(\cdot\mid h_t)
$$

Une action peut être : rechercher un document, appeler une API, demander confirmation, répondre ou **s'arrêter**.

**Pourquoi c'est important :** un agent ne connait pas nécessairement l'état réel. Un appel HTTP ayant expiré ne prouve pas que l'opération a échoué : le serveur peut l'avoir exécutée sans que sa réponse soit arrivée.

Dans ce document :

- les probabilités sont comprises entre 0 et 1 ;

- les couts monétaires sont exprimés en euros ;

- les latences sont exprimées en secondes ;

- les volumes de texte sont comptés en tokens ;

- 𝔼 désigne une espérance.

**Piège :** confondre l'historique observé avec une description complète et certaine du monde.

---

## 04  Vecteurs, produit scalaire et similarité cosinus

**Priorité : P0**

Un embedding représente un texte par un vecteur x∈ℝᵈ.

$$
x^\top y=\sum_{j=1}^{d}x_jy_j
$$

$$
\|x\|_2=\sqrt{\sum_{j=1}^{d}x_j^2}
$$

$$
\operatorname{cos}(x,y)=
\frac{x^\top y}{\|x\|_2\|y\|_2}
$$

Le produit scalaire mesure un alignement influencé par les normes. Le cosinus mesure l'orientation relative et appartient à [−1,1].

**Exemple :** pour x=(1,0) et y=(1,1), le cosinus vaut environ 0,707. Ces vecteurs sont partiellement alignés.

Si les embeddings sont normalisés à une norme de 1, le produit scalaire et le cosinus deviennent identiques.

**Application agentique :** rechercher les passages les plus proches d'une question, dédupliquer des mémoires ou identifier des requêtes similaires.

**Pourquoi connaitre la formule :** elle aide à comprendre les métriques d'une base vectorielle et à détecter un mauvais paramétrage.

**Pièges :**

- Un score de 0,8 ne signifie pas « 80 % de chances d'être pertinent ».
- Le cosinus est indéfini pour un vecteur nul.
- Les scores ne sont pas directement comparables entre tous les modèles d'embeddings.

---

## 05  Matrices : comprendre dimensions et transformations

**Priorité : P1**

Les modèles manipulent des lots de vecteurs à l'aide de matrices.

$$
Y=XW+b
$$

Avec :

$$
X\in\mathbb{R}^{n\times d}
$$

N représentations de dimension d ;

$$
W\in\mathbb{R}^{d\times m}
$$

Transformation apprise ;

- b∈ℝᵐ : biais ajouté à chaque ligne ;

$$
Y\in\mathbb{R}^{n\times m}
$$

Représentations transformées.

**Intuition :** une matrice mélange et repondère les coordonnées pour produire une autre représentation.

**Exemple :** 100 embeddings de dimension 768, transformés vers 256 dimensions, donnent une matrice de sortie 100×256.

**Application agentique :** comprendre les interfaces d'embeddings, les incompatibilités de dimensions et les mécanismes internes de l'attention.

**Pourquoi c'est important :** une erreur de dimension constitue souvent un problème d'architecture ou de versionnement, pas un problème de prompt.

**Piège :** deux modèles produisant chacun 768 coordonnées ne partagent pas nécessairement le même espace vectoriel. Après changement de modèle, il faut généralement recalculer l'index documentaire et réévaluer la recherche.

---

## 06  Probabilités conditionnelles et théorème de Bayes

**Priorité : P0**

$$
P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}
$$

Ici, A est un événement recherché et B une observation. Bayes combine une fréquence initiale avec la valeur informative de cette observation.

**Exemple : détecteur d'erreurs**

- 1 % des réponses sont erronées ;
- le détecteur signale 90 % des erreurs ;
- il signale aussi 5 % des réponses correctes.

$$
P(\text{erreur}\mid\text{signal})
=
\frac{0{,}90\times0{,}01}
{0{,}90\times0{,}01+0{,}05\times0{,}99}
\approx15{,}4\%
$$

Malgré une bonne sensibilité, la majorité des alertes sont ici de faux positifs, car les erreurs sont rares.

**Application agentique :** décider quelles réponses envoyer en revue humaine et estimer la valeur réelle d'un détecteur.

**Piège :** ignorer le taux de base. Autre piège : traiter « je suis sur à 95 % », produit par un LLM, comme une probabilité calibrée. Ce score doit être validé sur des résultats observés avant de guider une décision sensible.

---

## 07  Espérance et variance : prévoir sans masquer le risque

**Priorité : P0**

Pour une variable aléatoire discrète X :

$$
\mathbb{E}[X]=\sum_x xP(X=x)
$$

$$
\operatorname{Var}(X)=
\mathbb{E}\left[(X-\mathbb{E}[X])^2\right]
$$

L'espérance décrit le résultat moyen sur de nombreuses répétitions. La variance décrit la dispersion autour de cette moyenne.

**Exemple :** un agent résout 80 % des demandes pour 0,02 €. Les 20 % restants nécessitent une escalade coutant 1 € supplémentaire.

$$
\mathbb{E}[C]=0{,}02+0{,}20\times1=0{,}22\,€
$$

**Application agentique :** comparer des stratégies en tenant compte des appels, reprises, validations et traitements humains.

La linéarité de l'espérance reste valable même si les couts sont dépendants :

$$
\mathbb{E}[C_1+C_2]=\mathbb{E}[C_1]+\mathbb{E}[C_2]
$$

**Piège :** une moyenne acceptable peut cacher quelques incidents très couteux. Pour les actions financières ou destructrices, étudier également les cas extrêmes et les contraintes de sécurité. Une décision ne doit pas être fondée uniquement sur un cout moyen.

---

## 08  Logarithmes et entropie : mesurer une dispersion probabiliste

**Priorité : P1**

L'information associée à un événement de probabilité p peut s'écrire :

$$
I(p)=-\ln p
$$

L'entropie d'une distribution discrète est :

$$
H(P)=-\sum_i p_i\ln p_i
$$

Avec le logarithme naturel, l'unité est le **nat**. Avec un logarithme en base 2, l'unité est le bit. Par convention, 0ln0=0.

**Intuition :** une distribution concentrée sur une seule possibilité possède une faible entropie. Une distribution répartie entre plusieurs possibilités possède une entropie plus élevée.

**Exemple :** deux options équiprobables donnent une entropie de ln2≈0,693 nat. Une option certaine donne une entropie nulle.

**Application agentique :** analyser la diversité des choix ou le comportement d'un routeur probabiliste.

**Piège majeur :** l'entropie des prochains tokens n'est pas l'incertitude factuelle. Un modèle peut être très concentré sur une réponse fausse ou hésiter entre plusieurs formulations toutes correctes. Elle ne constitue donc pas, seule, un détecteur fiable d'hallucinations.

---

## 09  Softmax et température : transformer des scores en probabilités

**Priorité : P1**

Pour des scores zᵢ et une température T>0 :

$$
p_i=
\frac{\exp(z_i/T)}
{\sum_j\exp(z_j/T)}
$$

Une implémentation numériquement stable soustrait le score maximal m :

$$
p_i=
\frac{\exp((z_i-m)/T)}
{\sum_j\exp((z_j-m)/T)},
\qquad m=\max_j z_j
$$

Cette soustraction ne change pas les probabilités, mais évite certains débordements numériques.

**Intuition :**

- une température plus basse concentre la distribution ;
- une température plus haute l'aplatit ;
- lorsque T tend vers zéro, la masse se concentre sur les meilleurs scores.

**Application agentique :** régler la diversité de génération ou comprendre un routeur utilisant des probabilités de sélection.

**Exemple :** pour les scores 2 et 1, avec T=1, les probabilités sont environ 0,731 et 0,269.

**Complément : top-k et top-p (nucleus sampling).** Après la softmax, l'API peut tronquer la distribution avant le tirage. Top-k garde les k tokens les plus probables. Top-p garde le plus petit ensemble Vₚ des tokens les plus probables dont la masse atteint le seuil :

$$
\sum_{i\in V_p}p_i\geq p_{\text{top}},
\qquad
p_i'=\frac{p_i\,\mathbf 1(i\in V_p)}{\sum_{j\in V_p}p_j}
$$

**Exemple :** probabilités 0,5 ; 0,3 ; 0,15 ; 0,05 avec pₜₒₚ=0,8. On garde les deux premiers, renormalisés en 0,625 et 0,375. Les deux tokens improbables ne peuvent plus être tirés.

**Piège :** réduire la température ne garantit ni vérité ni reproductibilité complète. Les outils, le contexte, les versions et l'infrastructure introduisent aussi de la variabilité.

---

## 10  Génération autorégressive et vraisemblance

**Priorité : P1**

Un modèle de langage décompose la probabilité d'une séquence :

$$
P(x_{1:n}\mid c)=
\prod_{t=1}^{n}
P(x_t\mid x_{<t},c)
$$

Ici, c est le contexte et xₜ le token généré à l'étape t.

La perte logarithmique négative moyenne est :

$$
\operatorname{NLL}=
-\frac{1}{n}
\sum_{t=1}^{n}
\ln P(x_t\mid x_{<t},c)
$$

**Intuition :** le modèle apprend à attribuer davantage de probabilité aux tokens observés dans ses données d'entrainement.

**Application agentique :** comprendre pourquoi la génération dépend du préfixe, pourquoi une erreur précoce influence la suite et pourquoi la longueur affecte les probabilités brutes.

**Exemple :** dix tokens ayant chacun une probabilité conditionnelle de 0,5 donnent une probabilité de séquence de 0,5¹⁰≈0,000977.

**Complément : perplexité.** La métrique usuelle des modèles de langage est l'exponentielle de la NLL :

$$
\operatorname{PPL}=\exp(\operatorname{NLL})
$$

Dans l'exemple, NLL=ln2≈0,693, donc PPL=2 : le modèle hésite en moyenne autant qu'entre deux tokens équiprobables. Deux perplexités ne se comparent qu'avec le même tokenizer et le même texte.

**Piège :** la séquence la plus probable n'est pas nécessairement vraie, utile ou autorisée. Les comparaisons de NLL exigent des conventions compatibles, notamment pour la tokenisation et le traitement des longueurs.

---

## 11  Attention : sélectionner l'information dans le contexte

**Priorité : P1**

$$
\operatorname{Attention}(Q,K,V)=
\operatorname{softmax}
\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

Pour une séquence de longueur n :

$$
Q,K\in\mathbb{R}^{n\times d_k} ;
$$

$$
V\in\mathbb{R}^{n\times d_v} ;
$$

$$
QK^\top\in\mathbb{R}^{n\times n} ;
$$

- la softmax est appliquée par ligne.

**Intuition :** chaque position calcule dans quelle mesure elle doit utiliser les informations des autres positions. Le facteur √dₖ controle l'échelle des scores.

**Application agentique :** comprendre pourquoi la composition du contexte, les passages inutiles et leur position peuvent influencer les réponses.

Pour une attention dense standard, la matrice des interactions contient n² éléments. Doubler la longueur multiplie donc par quatre ce nombre d'interactions.

**Piège :** ce constat ne décrit pas universellement tous les modèles ou toutes les implémentations. Les noyaux optimisés, caches et variantes d'attention changent les couts effectifs. Enfin, une pondération d'attention élevée n'est pas une preuve de raisonnement correct.

---

## 12  Budget de tokens et cout d'inférence

**Priorité : P0**

Le contexte disponible impose une contrainte :

$$
n_{\text{système}}+
n_{\text{historique}}+
n_{\text{documents}}+
n_{\text{outils}}+
n_{\text{sortie réservée}}
\leq B
$$

Ici, B représente la capacité utilisable selon les limites du modèle et de son API.

Pour des tarifs au million de tokens :

$$
C_{\text{tokens}}=
\frac{
n_{\text{entrée}}r_{\text{entrée}}+
n_{\text{sortie}}r_{\text{sortie}}
}{10^6}
$$

**Exemple entièrement hypothétique :**

- 8 000 tokens d'entrée à 2 € par million ;
- 1 000 tokens de sortie à 8 € par million.

$$
C_{\text{tokens}}=
\frac{8000\times2+1000\times8}{10^6}
=0{,}024\,€
$$

**Application agentique :** fixer des budgets par tâche, limiter les boucles et choisir quand résumer la mémoire.

**Complément : cache de prompt.** Quand le début du contexte (système, outils, documents stables) est identique d'un appel à l'autre, le fournisseur peut le facturer à un tarif réduit :

$$
C_{\text{entrée}}=
\frac{
n_{\text{lu en cache}}\,r_{\text{cache}}+
n_{\text{écrit en cache}}\,r_{\text{écriture}}+
n_{\text{neuf}}\,r_{\text{entrée}}
}{10^6}
$$

**Exemple hypothétique :** sur les 8 000 tokens d'entrée, 6 000 sont lus en cache à 0,2 € par million (10 % du tarif normal). L'entrée coute (6000×0,2+2000×2)/10⁶=0,0052 € au lieu de 0,016 € ; l'appel complet passe de 0,024 € à 0,0132 €. Les ratios réels dépendent du fournisseur.

**Complément : latence d'un appel.**

$$
T_{\text{appel}}\approx T_{\text{TTFT}}+\frac{n_{\text{sortie}}}{v_{\text{décodage}}}
$$

$$
T_{\text{TTFT}}
$$

est le délai avant le premier token ;

$$
v_{\text{décodage}}
$$

le débit en tokens par seconde. Avec 0,6 s de TTFT et 1 000 tokens produits à 50 tokens/s, l'appel dure environ 20,6 s. **Ce sont les tokens de sortie qui dominent la latence**, pas ceux d'entrée.

**Piège :** ce cout exclut les outils, l'hébergement, les reprises et le travail humain. Les tarifs de raisonnement peuvent également modifier le calcul. Le cache ne fonctionne que si le préfixe est strictement identique : un horodatage placé au début du prompt système l'annule. Un budget tokens est une contrainte technique, pas une mesure de qualité.

---

## 12b  Boucle d'agent : le contexte cumulé coute plus que prévu

**Priorité : P0**

Dans une boucle d'agent, chaque tour renvoie au modèle **tout** le contexte accumulé : instructions, définitions d'outils, puis chaque appel d'outil et son résultat. Si le contexte initial vaut n₀ tokens et que chaque tour ajoute Δ tokens, le tour t lit n₀+(t−1)Δ tokens. Sur T tours :

$$
N_{\text{entrée}}=
\sum_{t=1}^{T}\bigl(n_0+(t-1)\Delta\bigr)
=
Tn_0+\Delta\frac{T(T-1)}{2}
$$

Le terme en T² domine vite. Le contexte doit aussi tenir dans la fenêtre B :

$$
T_{\max}=\left\lfloor\frac{B-n_0}{\Delta}\right\rfloor+1
$$

**Exemple :** n₀=3000, Δ=1500.

- T=10 : 30 000+1500×45=97 500 tokens d'entrée, soit 0,195 € à 2 € par million.
- T=20 : 60 000+1500×190=345 000 tokens, soit 0,69 €.

**Doubler le nombre de tours multiplie ici le cout d'entrée par environ 3,5.**

**Application agentique :** plafonner le nombre de tours, tronquer ou résumer les résultats d'outils volumineux, garder un préfixe stable pour profiter du cache, confier une sous-tâche à un sous-agent qui repart d'un contexte vierge et ne renvoie qu'un résumé.

**Piège :** résumer réduit Δ mais peut effacer une incertitude ou un fait utile (voir 20). Le cout réel dépend aussi du cache : avec un préfixe caché, la croissance reste quadratique mais à un tarif plus faible.

---

## 13  Recherche lexicale : TF-IDF et BM25

**Priorité : P0 pour le RAG**

TF-IDF combine fréquence locale d'un terme et rareté documentaire :

$$
w(t,d)=\operatorname{tf}(t,d)\operatorname{idf}(t)
$$

Une formulation courante de BM25 est :

$$
\operatorname{BM25}(q,d)=
\sum_{t\in q}
\operatorname{IDF}(t)
\frac{
f(t,d)(k_1+1)
}{
f(t,d)+k_1\left(1-b+b\frac{L_d}{\overline L}\right)
}
$$

$$
\operatorname{IDF}(t)=
\ln\left(1+
\frac{N-\operatorname{df}(t)+0{,}5}
{\operatorname{df}(t)+0{,}5}
\right)
$$

- f(t,d) : fréquence du terme dans le document ;

- N : nombre de documents ;

- df(t) : nombre de documents contenant le terme ;

$$
L_d,\overline L
$$

Longueur du document et longueur moyenne ;

- k₁ : saturation de fréquence ;

- b : correction de longueur.

**Application :** retrouver précisément « HTTP 429 », une référence contractuelle ou un identifiant Java.

**Pourquoi c'est important :** les embeddings ne remplacent pas la correspondance lexicale exacte.

**Piège :** un score BM25 n'est pas une probabilité. La tokenisation, la langue et l'unité d'indexation influencent fortement les résultats.

---

## 14  Recherche hybride et Reciprocal Rank Fusion

**Priorité : P0 pour le RAG**

La recherche dense rapproche les significations via les embeddings. La recherche lexicale retrouve les correspondances de termes. Leur combinaison améliore souvent la couverture, mais doit être évaluée.

Pour fusionner plusieurs classements :

$$
\operatorname{RRF}(d)=
\sum_{j:\,d\in R_j}
\frac{1}{k_{\text{RRF}}+\operatorname{rang}_j(d)}
$$

- Rⱼ : classement produit par le moteur j ;

- rangⱼ(d) : position du document, à partir de 1 ;

$$
k_{\text{RRF}}>0
$$

Constante d'amortissement.

**Exemple :** avec

$$
k_{\text{RRF}}=60 ,
$$

un document classé premier par deux moteurs reçoit :

$$
\frac{1}{61}+\frac{1}{61}\approx0{,}0328
$$

**Pourquoi c'est utile :** RRF évite de supposer que les scores BM25 et cosinus possèdent la même échelle.

**Pièges :**

$$
k_{\text{RRF}}
$$

n'est pas le nombre de résultats à retourner.

- Deux moteurs très similaires peuvent renforcer les mêmes erreurs.

- La fusion ne remplace pas le controle d'accès : les documents interdits doivent être filtrés avant exposition à l'agent.

---

## 15  Precision@k et Recall@k : mesurer la récupération

**Priorité : P0**

Soient :

- Rₖ : les k premiers documents retournés ;
- G : l'ensemble des documents pertinents connus.

$$
\operatorname{Precision@k}=
\frac{|R_k\cap G|}{k}
$$

$$
\operatorname{Recall@k}=
\frac{|R_k\cap G|}{|G|}
$$

Ces définitions supposent ici que k résultats sont retournés et que G n'est pas vide.

**Exemple :** sur 5 résultats, 3 sont pertinents. Le corpus contient 6 documents pertinents.

$$
\operatorname{Precision@5}=0{,}6,
\qquad
\operatorname{Recall@5}=0{,}5
$$

**Intuition :**

- la précision mesure la proportion de bons résultats fournis ;
- le rappel mesure la proportion des bons résultats retrouvés.

**Complément : Hit@k et MRR.** Sur un ensemble de requêtes Q, avec

$$
\operatorname{rang}_q
$$

la position du **premier** document pertinent :

$$
\operatorname{Hit@k}=\frac{1}{|Q|}\sum_{q\in Q}\mathbf 1(\operatorname{rang}_q\leq k),
\qquad
\operatorname{MRR}=\frac{1}{|Q|}\sum_{q\in Q}\frac{1}{\operatorname{rang}_q}
$$

Par convention,

$$
1/\operatorname{rang}_q=0
$$

si aucun pertinent n'est retrouvé dans la liste évaluée.

**Exemple :** trois requêtes ; premier pertinent en position 1, en position 3, absent. Hit@5=2/3 et MRR=(1+1/3+0)/3≈0,444. Le MRR est la bonne métrique quand l'agent n'exploite réellement que le premier bon passage.

**Application agentique :** augmenter le rappel pour éviter de manquer une clause critique, puis améliorer la précision pour réduire le bruit et les tokens.

**Piège :** si les annotations de pertinence sont incomplètes, le rappel est imparfaitement estimé. Et une recherche excellente ne garantit pas que l'agent utilisera correctement les passages récupérés.

---

## 16  NDCG et chunking : classer puis sélectionner

**Priorité : P0 pour le RAG**

Lorsque la pertinence est graduée :

$$
\operatorname{DCG@k}=
\sum_{i=1}^{k}
\frac{2^{\operatorname{rel}_i}-1}{\log_2(i+1)}
$$

$$
\operatorname{NDCG@k}=
\frac{\operatorname{DCG@k}}{\operatorname{IDCG@k}}
$$

relᵢ est la pertinence du résultat en position i. IDCG est le score du classement idéal sur le même ensemble de référence.

Si IDCG vaut zéro, il faut fixer une convention explicite : par exemple retourner zéro et signaler ces cas séparément.

**Intuition :** un passage très pertinent placé en tête vaut davantage que le même passage placé loin dans la liste.

Pour construire le contexte :

$$
\sum_{d\in S}\operatorname{tokens}(d)\leq B_{\text{documents}}
$$

**Application :** sélectionner des chunks utiles dans une enveloppe de tokens.

**Complément : MMR, pour éviter les doublons.** Cinq chunks presque identiques remplissent le budget sans apporter d'information. La Maximal Marginal Relevance choisit itérativement, parmi les candidats R non encore retenus, celui qui est proche de la question q mais éloigné de la sélection S :

$$
d^\star=
\arg\max_{d\in R\setminus S}
\left[
\lambda_{\text{MMR}}\operatorname{sim}(d,q)
-(1-\lambda_{\text{MMR}})\max_{d'\in S}\operatorname{sim}(d,d')
\right]
$$

**Exemple :** d₁ est déjà retenu. d₂ a une similarité de 0,88 avec la question mais de 0,95 avec d₁ ; d₃ a 0,75 avec la question et 0,30 avec d₁. Avec

$$
\lambda_{\text{MMR}}=0{,}7
$$

D₂ obtient 0,616−0,285=0,331, d₃ obtient 0,525−0,09=0,435. On retient d₃.

**Piège :** aucune taille de chunk n'est universellement optimale. Des fragments courts améliorent parfois la précision mais perdent du contexte ; des fragments longs préservent le sens mais augmentent le bruit. Évaluer conjointement segmentation, classement et réponse finale.

---

## 16b  Mémoire d'agent : récence, importance et pertinence

**Priorité : P1, P0 si l'agent garde une mémoire longue**

Une mémoire longue ne se relit pas en entier : elle se classe. Un score courant combine trois composantes ramenées sur [0,1] :

$$
\operatorname{score}(m)=
\alpha\,\operatorname{récence}(m)
+\beta\,\operatorname{importance}(m)
+\gamma\,\operatorname{pertinence}(m,q)
$$

$$
\operatorname{récence}(m)=\delta^{\,\Delta t_m},
\qquad
t_{1/2}=\frac{\ln2}{\ln(1/\delta)}
$$

- Δ tₘ : temps écoulé depuis le dernier accès à la mémoire m ;
- δ∈(0,1) : facteur d'oubli par unité de temps ;

$$
t_{1/2}
$$

Demi-vie, durée après laquelle la récence est divisée par deux ;
- pertinence : souvent le cosinus de la diapositive 04.

**Exemple :** δ=0,995 par heure donne une demi-vie d'environ 138 heures, soit 5,8 jours. Avec α=β=γ=1 :

- mémoire A : vue il y a 2 h, importance 0,3, cosinus 0,6 → 0,990+0,3+0,6=1,890 ;
- mémoire B : vue il y a 72 h, importance 0,9, cosinus 0,8 → 0,697+0,9+0,8=2,397.

B passe devant malgré son âge.

**Application agentique :** choisir les souvenirs injectés dans le contexte, décider quoi résumer, archiver ou oublier.

**Pièges :** si les trois composantes n'ont pas la même échelle, l'une écrase les autres. Une importance notée par le LLM n'est pas calibrée. « Oublier » dans le classement n'est pas supprimer : une demande d'effacement de données personnelles exige une vraie suppression. Le déroulé complet est dans `04-Contexte-Similarite-et-Memoire/16-Memoire-Formule-Decroissance-Temporelle.md`.

---

## 17  Grounding : vérifier les affirmations, pas seulement les citations

**Priorité : P0**

Une mesure simple du support documentaire est :

$$
\operatorname{TauxSupport}=
\frac{
\text{affirmations vérifiables correctement étayées}
}{
\text{affirmations vérifiables évaluées}
}
$$

Il faut définir ce qu'est une affirmation, ce qu'est un support suffisant et comment traiter les contradictions.

**Exemple :** une réponse contient dix affirmations vérifiables. Huit sont réellement justifiées par les sources citées : le taux de support vaut 80 %.

**Application agentique :** mesurer la fidélité documentaire d'un assistant juridique, technique ou de support.

Une vérification utile examine :

1. l'existence de la source ;
2. l'accès autorisé à cette source ;
3. le passage exact cité ;
4. son implication réelle pour l'affirmation ;
5. sa date et sa validité.

**Piège :** un document pertinent peut être faux ou obsolète. Une citation réelle peut ne pas soutenir la phrase associée. Enfin, découper artificiellement les affirmations peut gonfler la métrique : le protocole d'annotation doit rester stable et auditable.

---

## 18  Utilité espérée : choisir une action sous contraintes

**Priorité : P0**

Une politique peut chercher à maximiser une utilité attendue :

$$
a^\star=
\arg\max_{a\in\mathcal A_{\text{autorisée}}(h)}
\mathbb{E}\left[
U(a)\mid h
\right]
$$

Une utilité composite possible est :

$$
U(a)=
w_qQ(a)
-w_c\frac{C(a)}{C_0}
-w_t\frac{T(a)}{T_0}
-w_rR(a)
$$

- Q : qualité ;
- C,T : cout et latence ;
- C₀,T₀ : échelles de normalisation ;
- R : risque ;
- w : préférences métier.

**Intuition :** une action plus chère peut être préférable si elle apporte une amélioration suffisamment importante.

**Application :** choisir entre répondre immédiatement, rechercher une source supplémentaire ou escalader.

**Piège majeur :** une action interdite ne doit pas devenir acceptable parce qu'elle obtient un bon score global. L'autorisation relève de l'ensemble des actions permises, pas simplement d'une pénalité.

Les poids ne sont pas des constantes scientifiques : ils traduisent des arbitrages métier qui doivent être discutés et testés.

---

## 19  MDP et équation de Bellman : raisonner sur les conséquences

**Priorité : P1**

Un processus de décision markovien, ou MDP, suppose que l'état courant contient l'information nécessaire aux transitions futures.

$$
V^\star(s)=
\max_a
\sum_{s'}
P(s'\mid s,a)
\left[
r(s,a,s')+\gamma V^\star(s')
\right]
$$

- V\*(s) : meilleure valeur future depuis s ;

- P(s'| s,a) : transition ;

- r : récompense immédiate ;

- γ∈[0,1) : actualisation dans un cadre infini usuel.

**Intuition :** une bonne action ne se juge pas seulement à son résultat immédiat, mais aux possibilités qu'elle ouvre ensuite.

**Application :** une recherche supplémentaire coute maintenant, mais peut éviter une erreur couteuse lors de l'appel d'un outil.

**Piège :** un historique textuel n'est pas automatiquement un état markovien. Les agents travaillent souvent en observation partielle : statut réel d'une commande inconnu, information manquante ou utilisateur ambigu.

Bellman fournit un cadre conceptuel. Il ne signifie pas qu'il faut implémenter un solveur MDP pour chaque assistant de production.

---

## 20  POMDP : maintenir une croyance sur un état caché

**Priorité : P1 avancé**

Dans un environnement partiellement observable, l'agent peut maintenir une distribution de croyance :

$$
b_t(s)=P(s_t=s\mid h_t)
$$

Après l'action aₜ et l'observation oₜ₊₁ :

$$
b_{t+1}(s')=
\frac{
O(o_{t+1}\mid s',a_t)
\sum_s P(s'\mid s,a_t)b_t(s)
}{
Z
}
$$

O est la vraisemblance de l'observation ; Z normalise la distribution pour que sa somme vaille 1.

**Intuition :** prédire d'abord ce qui a pu changer, puis corriger cette prédiction avec les nouvelles observations.

**Exemple :** après un timeout sur un paiement, conserver les hypothèses « exécuté » et « non exécuté », puis consulter le statut avant de réessayer.

**Application pratique :** on utilise souvent un état structuré contenant faits confirmés, hypothèses et inconnues plutot qu'une distribution exacte.

**Piège :** un résumé conversationnel peut effacer l'incertitude. « Le paiement a probablement échoué » ne doit pas devenir automatiquement « le paiement a échoué » dans la mémoire suivante.

---

## 21  Arrêt et valeur de l'information : savoir quand ne plus agir

**Priorité : P0 pour l'arrêt, P1 pour l'EVSI**

Continuer n'est utile que si le gain attendu dépasse les couts supplémentaires :

$$
\Delta V_{\text{attendue}}
C_{\text{monétaire}}
+C_{\text{latence}}
+C_{\text{risque}}
$$

Tous les termes doivent être exprimés dans une unité d'utilité commune.

La valeur attendue d'une information supplémentaire est :

$$
\operatorname{EVSI}=
\mathbb{E}_o
\left[
\max_a\mathbb{E}[U(a)\mid o]
\right]
-
\max_a\mathbb{E}[U(a)]
$$

**Exemple :** agir maintenant donne un gain de 10 € si l'action est correcte, une perte de 20 € sinon. Sa probabilité de correction est 0,8.

$$
\mathbb{E}[U]=0{,}8\times10-0{,}2\times20=4\,€
$$

Supposons que s'abstenir rapporte 0 €. Une information parfaite permettrait d'agir uniquement dans les bons cas : valeur attendue 0,8×10=8 €, soit une valeur de l'information parfaite (**EVPI**) de 4 €. C'est le cas limite de la formule d'EVSI, lorsque l'observation révèle complètement l'état pertinent. Si cette vérification parfaite coute 1 €, son gain net attendu est 3 €.

**Piège :** un humain ou un outil n'apporte presque jamais une information parfaite. Estimer son efficacité réelle et prévoir une limite de boucle.

---

## 22  Bandits et UCB1 : explorer sans choisir au hasard

**Priorité : P1**

Pour sélectionner une option i, UCB1 utilise :

$$
\operatorname{UCB}_i(t)=
\overline r_i+
\sqrt{\frac{2\ln t}{n_i}}
$$

- r̅ᵢ : récompense moyenne observée ;
- nᵢ : nombre de sélections de l'option ;
- t : nombre total de sélections.

Chaque option doit d'abord être essayée pour éviter nᵢ=0.

**Intuition :** choisir une option qui fonctionne bien, mais accorder aussi une chance aux options encore peu connues.

**Application agentique :** sélectionner entre plusieurs stratégies de recherche ou modèles déjà validés.

La forme classique suppose notamment des récompenses bornées dans [0,1] et un environnement stationnaire.

**Exemple :** deux routeurs ont des scores moyens proches. Celui qui n'a été testé que dix fois reçoit un bonus d'exploration supérieur à celui testé mille fois.

**Piège :** ne jamais explorer librement des actions dangereuses sur des utilisateurs. Les changements de trafic, de modèle ou de documentation violent aussi la stationnarité. L'exploration doit rester dans un périmètre autorisé et surveillé.

---

## 23  Fiabilité composée : les erreurs se multiplient

**Priorité : P0**

Pour réussir une chaine de m étapes :

$$
P\left(\bigcap_{i=1}^{m}S_i\right)
=
P(S_1)
\prod_{i=2}^{m}
P(S_i\mid S_1,\ldots,S_{i-1})
$$

Cette formule est générale. Si les étapes sont indépendantes et ont toutes une probabilité de succès p :

$$
P(\text{succès global})=p^m
$$

**Exemple :** dix étapes indépendantes fiables à 95 % donnent :

$$
0{,}95^{10}\approx59{,}9\%
$$

Pour plusieurs voies indépendantes, dont une seule doit réussir :

$$
P(\text{au moins un succès})=
1-\prod_i(1-p_i)
$$

**Complément : vote majoritaire (self-consistency, jury de juges).** Pour n votants indépendants, n impair, chacun correct avec probabilité p :

$$
P(\text{majorité correcte})=
\sum_{k=(n+1)/2}^{n}\binom{n}{k}p^k(1-p)^{n-k}
$$

**Exemple :** avec p=0,7, trois votes donnent 0,784 et cinq votes 0,837. Le gain ralentit vite, alors que le cout croît linéairement. Si p<0,5, le vote **aggrave** l'erreur.

**Application agentique :** comprendre pourquoi ajouter des étapes ou des agents peut réduire la fiabilité au lieu de l'améliorer.

**Piège :** les erreurs sont souvent corrélées. Trois agents utilisant le même modèle, les mêmes sources et le même mauvais postulat ne constituent pas trois protections indépendantes.

La redondance est surtout utile lorsque les méthodes de vérification apportent des informations réellement différentes : tests exécutables, controle de schéma, source indépendante ou validation humaine.

---

## 24  Retries : améliorer la disponibilité sans répéter les dégâts

**Priorité : P0**

Pour des tentatives indépendantes ayant chacune une probabilité de succès p, avec au maximum r tentatives :

$$
P(\text{succès})=1-(1-p)^r
$$

Si l'on s'arrête au premier succès :

$$
\mathbb{E}[N]=
\sum_{j=0}^{r-1}(1-p)^j
=
\frac{1-(1-p)^r}{p}
$$

Pour p=0,8 et r=3 :

$$
P(\text{succès})=0{,}992,
\qquad
\mathbb{E}[N]=1{,}24
$$

**Application :** estimer le bénéfice et le cout moyen des reprises sur une API temporairement indisponible.

**Pièges :**

- Une erreur déterministe ne disparait pas en répétant le même appel.
- Une panne commune rend les tentatives dépendantes.
- Un timeout ne signifie pas absence d'exécution.

Pour une opération financière ou une création de ressource, utiliser une clé d'idempotence, consulter le statut et définir une politique de compensation. Ajouter backoff, jitter et budget global pour éviter les tempêtes de retries.

**Complément : backoff exponentiel avec jitter complet.** Avant la reprise numéro j (j=0,1,…) :

$$
d_j\sim\mathcal U\left(0,\ \min\left(d_{\max},\ d_0\cdot2^{j}\right)\right)
$$

**Exemple :** d₀=0,5 s et dₘₐₓ=8 s donnent des plafonds de 0,5 ; 1 ; 2 ; 4 ; 8 s. Sur cinq reprises, l'attente cumulée vaut au plus 15,5 s et en moyenne la moitié, 7,75 s. Le tirage aléatoire évite que mille clients rejettent leurs requêtes au même instant. Si l'API renvoie un en-tête `Retry-After` (HTTP 429 ou 503), il prime sur la formule.

---

## 25  Orchestration : cout total et chemin critique

**Priorité : P0**

Pour une exécution représentée par un graphe de dépendances :

$$
T_{\text{total}}\approx
\max_{p\in\mathcal P}
\sum_{i\in p}T_i
$$

𝒫 est l'ensemble des chemins du début à la fin. Le plus long est le **chemin critique**.

En revanche, le cout des appels reste approximativement additif :

$$
C_{\text{total}}=
\sum_i C_i+C_{\text{orchestration}}
$$

**Exemple :** trois recherches indépendantes durent 2, 3 et 4 secondes. Une synthèse finale prend 1 seconde.

- Exécution séquentielle : 2+3+4+1=10 secondes.
- Exécution parallèle idéale : max(2,3,4)+1=5 secondes.

**Application agentique :** paralléliser des recherches indépendantes et éviter de paralléliser des étapes réellement dépendantes.

**Piège :** le gain de latence ne réduit pas automatiquement le cout. Les quotas, la contention, les connexions et la coordination ajoutent du délai.

Si les durées sont aléatoires, mesurer directement la distribution du chemin critique : le maximum de plusieurs latences peut augmenter la fréquence des résultats lents.

---

## 26  Files d'attente : pourquoi un agent ralentit brutalement

**Priorité : P1, souvent indispensable à l'échelle**

La loi de Little relie :

$$
L=\lambda W
$$

- L : nombre moyen de requêtes présentes ;
- λ : débit moyen ;
- W : temps moyen passé dans le système.

**Exemple :** avec 10 demandes par seconde et un temps moyen de 2 secondes, le système contient en moyenne 20 demandes en cours.

Dans un modèle M/M/1 stable :

$$
W=\frac{1}{\mu-\lambda},
\qquad \lambda<\mu
$$

μ est le taux de service d'un serveur unique.

Pour μ=10 requêtes/seconde :

- à λ=5, W=0,2 seconde ;
- à λ=9, W=1 seconde ;
- à λ=9,9, W=10 secondes.

Passer de 90 % à 99 % d'occupation multiplie l'attente par dix : c'est le « mur » de la saturation, avec ρ=λ/μ le taux d'occupation et

$$
W=\frac{1}{\mu}\cdot\frac{1}{1-\rho} .
$$

**Application agentique :** dimensionner workers, files, limites de concurrence et mécanismes de backpressure.

**Piège :** M/M/1 suppose notamment des arrivées de Poisson et des durées exponentielles. Un service LLM réel peut s'en éloigner fortement. Ces formules ne donnent pas directement le p95, ni les effets des quotas de tokens.

---

## 27  Taux de réussite et intervalle de Wilson

**Priorité : P0**

Pour s réussites sur n tâches :

$$
\widehat p=\frac{s}{n}
$$

Une approximation de l'erreur standard est :

$$
\operatorname{SE}(\widehat p)=
\sqrt{\frac{\widehat p(1-\widehat p)}{n}}
$$

L'intervalle de Wilson est généralement plus robuste qu'un intervalle symétrique naïf :

$$
\frac{
\widehat p+\frac{z^2}{2n}
\ \pm\
z\sqrt{
\frac{\widehat p(1-\widehat p)}{n}
+\frac{z^2}{4n^2}
}
}{
1+\frac{z^2}{n}
}
$$

Pour un niveau nominal de 95 %, z≈1,96.

**Exemple :** 90 réussites sur 100 donnent un taux de 90 %, avec un intervalle de Wilson d'environ **82,6 % à 94,5 %**.

**Application :** éviter d'annoncer une précision artificielle à partir d'un petit benchmark.

**Piège :** cet intervalle suppose un échantillonnage compatible avec un modèle binomial. Cent variantes presque identiques d'une même tâche n'apportent pas l'information de cent tâches indépendantes. L'intervalle ne corrige pas non plus un benchmark non représentatif.

---

## 27b  pass@k et pass^k : réussir une fois ou réussir à chaque fois

**Priorité : P0**

Un agent est stochastique : la même tâche, relancée, ne réussit pas toujours. On lance n essais par tâche et on compte c réussites. Deux questions différentes se posent.

**pass@k** : au moins un succès parmi k essais (utile si un test automatique ou un humain choisit le bon). Estimateur sans biais :

$$
\operatorname{pass@}k=
\mathbb{E}_{\text{tâches}}
\left[
1-\frac{\binom{n-c}{k}}{\binom{n}{k}}
\right]
$$

**pass^k** : **tous** les k essais réussissent (ce que vit un client qui revient k fois avec la même demande) :

$$
\operatorname{pass}^k=
\mathbb{E}_{\text{tâches}}
\left[
\frac{\binom{c}{k}}{\binom{n}{k}}
\right]
\approx \widehat p^{\,k}
$$

**Exemple :** une tâche, n=10 essais, c=7 réussites.

- pass@1=pass¹=0,7 ;

$$
\operatorname{pass@}3=1-\binom{3}{3}/\binom{10}{3}=1-1/120\approx0{,}992 ;
$$

$$
\operatorname{pass}^3=\binom{7}{3}/\binom{10}{3}=35/120\approx0{,}292 .
$$

Le même agent paraît excellent selon pass@3 et peu fiable selon pass^3.

**Application agentique :** pass@k mesure une **capacité** (génération de code avec tests, recherche avec vérificateur). pass^k mesure la **constance** attendue en production, notamment pour un agent de support ou de transaction.

**Piège :** l'estimateur exige n≥ k. Annoncer pass@k sans dire qui sélectionne le bon essai, ou sans compter le cout des k essais, embellit le résultat.

---

## 28  Taille d'échantillon et comparaison A/B

**Priorité : P0**

Pour estimer une proportion avec une marge approximative e :

$$
n\approx\frac{z^2p(1-p)}{e^2}
$$

Avec p=0,5, z=1,96 et e=0,05 :

$$
n\approx384{,}16
$$

On arrondit à **385 observations indépendantes**. Ce calcul concerne une proportion isolée, pas la puissance d'un test A/B.

Pour deux groupes indépendants :

$$
\widehat\Delta=\widehat p_B-\widehat p_A
$$

$$
\operatorname{SE}(\widehat\Delta)=
\sqrt{
\frac{\widehat p_A(1-\widehat p_A)}{n_A}
+
\frac{\widehat p_B(1-\widehat p_B)}{n_B}
}
$$

Un intervalle approximatif est Δ̂± zSE, sous conditions d'effectifs suffisants.

**Application :** comparer deux versions d'agent.

**Pièges :**

- Si les deux versions traitent les mêmes tâches, les résultats sont appariés : préférer McNemar pour du binaire ou un bootstrap apparié adapté (voir ci-dessous).
- Les tests répétés et comparaisons multiples augmentent les fausses alertes.
- Une différence observée n'établit pas une causalité sans protocole expérimental approprié.

**Complément : test de McNemar pour deux versions sur les mêmes tâches.** Seules les paires **discordantes** comptent : b tâches réussies par A et ratées par B, c tâches ratées par A et réussies par B.

$$
\chi^2=\frac{(|b-c|-1)^2}{b+c}
$$

On compare à 3,84 (seuil à 5 %, un degré de liberté).

**Exemple :** 200 tâches, b=12, c=28. χ²=15²/40≈5,63>3,84 : B fait mieux de façon significative. Les 160 tâches où A et B ont le même résultat n'apportent aucune information sur leur différence. Si b+c<25, utiliser le test binomial exact.

---

## 29  Matrice de confusion, précision, rappel et F1

**Priorité : P0**

Considérons « nécessite une escalade » comme classe positive :

- TP : escalade correctement déclenchée ;
- FP : escalade inutile ;
- FN : escalade nécessaire mais manquée ;
- TN : traitement autonome approprié.

$$
\operatorname{Précision}=
\frac{TP}{TP+FP}
$$

$$
\operatorname{Rappel}=
\frac{TP}{TP+FN}
$$

$$
F_1=
\frac{2PR}{P+R}
$$

Ici, P et R représentent précision et rappel.

**Exemple :** TP=40, FP=10, FN=20. La précision vaut 80 %, le rappel environ 66,7 %, et F1 environ 72,7 %.

**Application agentique :** évaluer un détecteur d'incertitude, un filtre de sécurité ou une règle d'escalade.

**Pourquoi c'est important :** augmenter le rappel protège contre les demandes risquées manquées, mais peut saturer les équipes humaines.

**Piège :** F1 ignore les vrais négatifs et les couts asymétriques. Une métrique élevée peut masquer une erreur rare mais catastrophique. Les dénominateurs nuls doivent recevoir une convention explicite dans les rapports.

---

## 29b  LLM juge : mesurer son accord avec les humains

**Priorité : P0 dès qu'un LLM note les réponses**

Un LLM utilisé comme évaluateur est lui-même un classifieur : il faut le mesurer avant de lui confier l'évaluation. Le pourcentage d'accord pₒ surestime la qualité, car deux évaluateurs d'accord au hasard le seraient souvent. Le kappa de Cohen corrige cet effet :

$$
\kappa=\frac{p_o-p_e}{1-p_e},
\qquad
p_e=\sum_{c}p_{\text{humain}}(c)\,p_{\text{juge}}(c)
$$

**Exemple :** 100 réponses annotées. L'humain juge 80 réponses correctes, le LLM 85 ; ils sont d'accord sur 85 cas (75 « correct », 10 « incorrect »).

$$
p_e=0{,}80\times0{,}85+0{,}20\times0{,}15=0{,}71,
\qquad
\kappa=\frac{0{,}85-0{,}71}{1-0{,}71}\approx0{,}48
$$

85 % d'accord, mais un kappa seulement **modéré** : le juge laisse passer la moitié des réponses que l'humain rejette (10 sur 20).

**Application agentique :** valider un juge sur un échantillon annoté avant de l'utiliser en CI, et suivre aussi son rappel sur la classe « incorrect ».

**Pièges :** biais de position (préférer la première réponse), de longueur, d'auto-préférence pour les sorties du même modèle. Mesurer κ par catégorie de tâche et rejouer la mesure à chaque changement de modèle ou de prompt du juge.

---

## 30 Calibration, score de Brier et seuil économique

**Priorité : P0 si les scores pilotent des actions**

Pour des probabilités prédites pᵢ et des résultats yᵢ∈{0,1} :

$$
\operatorname{Brier}=
\frac1n\sum_{i=1}^{n}(p_i-y_i)^2
$$

Une bonne calibration signifie, par exemple, que les cas annoncés à 80 % se réalisent environ 80 % du temps.

**Attention :** le score de Brier dépend aussi de la capacité à distinguer les cas ; il ne mesure pas exclusivement la calibration.

Pour mesurer la calibration seule, on regroupe les prédictions en M intervalles de confiance Bₘ et on calcule l'**erreur de calibration attendue** :

$$
\operatorname{ECE}=
\sum_{m=1}^{M}\frac{|B_m|}{n}
\left|\operatorname{acc}(B_m)-\operatorname{conf}(B_m)\right|
$$

**Exemple :** 60 cas annoncés vers 90 % ne sont corrects qu'à 72 % ; 40 cas annoncés vers 60 % le sont à 55 %. ECE=0,6×0,18+0,4×0,05=0,128 : le système est surconfiant de 12,8 points en moyenne. La valeur dépend du découpage en intervalles, qu'il faut fixer et documenter.

Si ρ est la prévalence :

$$
\mathbb{E}[L]=
C_{FP}(1-\rho)\operatorname{FPR}
+
C_{FN}\rho\operatorname{FNR}
$$

Pour une probabilité calibrée p=P(y=1| x), avec uniquement des couts d'erreur :

$$
\text{prédire positif si }
p>
\frac{C_{FP}}{C_{FP}+C_{FN}}
$$

**Exemple :** si manquer un cas coute 100 et une fausse alerte coute 1, le seuil vaut environ 0,0099.

**Piège :** ce seuil change si les actions ont d'autres couts, si les probabilités sont mal calibrées ou si la capacité de revue est limitée.

---

## 31 Sécurité : mesurer les incidents sans remplacer l'autorisation

**Priorité : P0**

Une métrique empirique simple est :

$$
\widehat p_{\text{incident}}=
\frac{\text{actions interdites observées}}
{\text{opportunités évaluées}}
$$

**Exemple :** zéro incident sur 1 000 essais ne prouve pas un risque nul. Sous hypothèses binomiales, la « règle de trois » donne une borne supérieure approximative à 95 % de 3/1000, soit 0,3 %.

Cette approximation ne garantit rien sur des attaques nouvelles ou un changement de distribution.

**Application agentique :** mesurer les échecs des protections tout en conservant des controles exécutoires :

- permissions calculées coté serveur ;
- validation des paramètres ;
- séparation lecture/écriture ;
- sandbox ;
- limites de montant et de portée ;
- confirmation humaine ;
- journal d'audit.

**Piège :** demander au modèle « n'exécute jamais une action interdite » n'est pas une politique d'autorisation. Le modèle peut proposer une action ; un composant de confiance doit décider si son exécution est permise.

Les garanties restent limitées à la correction du mécanisme et à son modèle de menace.

---

## 32 Robustesse : regarder la queue de distribution

**Priorité : P1**

La moyenne ne suffit pas pour la latence, le cout ou les pertes. Examiner aussi :

- médiane et p95 ;
- taux d'échec par langue, client et type de tâche ;
- incidents rares ;
- évolution temporelle ;
- taille des sous-groupes évalués.

Pour une perte L, la CVaR de queue supérieure peut s'écrire :

$$
\operatorname{CVaR}_{\alpha}(L)=
\min_{\eta}
\left[
\eta+
\frac{1}{1-\alpha}
\mathbb{E}\left[(L-\eta)_+\right]
\right]
$$

où (x)₊=max(x,0), et α est le niveau de queue.

**Intuition :** à α=0,95, on s'intéresse aux pertes de la partie la plus défavorable de la distribution, avec un traitement mathématique approprié des masses de probabilité.

**Application :** comparer deux agents ayant le même cout moyen mais des incidents extrêmes différents.

**Piège :** les queues nécessitent beaucoup de données. Sur 100 observations, les 5 % les plus défavorables ne représentent que cinq cas. Une estimation précise en apparence peut être très instable.

---

## 33 Descente de gradient : comment les paramètres sont ajustés

**Priorité : P2**

Pour une fonction de perte ℒ(θ) :

$$
\theta_{k+1}=
\theta_k-
\eta\nabla_\theta\mathcal L(\theta_k)
$$

- θ : paramètres du modèle ;

$$
\nabla_\theta\mathcal L
$$

Gradient ;

- η>0 : taux d'apprentissage.

**Intuition :** modifier les paramètres dans une direction qui réduit localement la perte.

**Exemple :** avec ℒ(θ)=θ², θ₀=2 et η=0,1, le gradient vaut 2θ₀=4 ; le nouveau paramètre vaut donc 2−0,1×4=1,6.

**Application agentique :** comprendre le fine-tuning d'un modèle spécialisé, d'un classifieur de routage ou d'un reranker.

**Pourquoi ce n'est pas la première priorité :** de nombreux problèmes proviennent d'outils mal conçus, de sources incomplètes ou d'une mauvaise évaluation. L'entrainement ne corrige pas automatiquement ces défauts.

**Pièges :** un taux trop élevé peut déstabiliser l'optimisation ; un taux trop faible ralentit l'apprentissage. Une perte d'entrainement qui diminue ne garantit pas une amélioration sur les tâches réelles.

---

## 34  Entropie croisée et divergence KL

**Priorité : P2**

Pour une distribution cible P et une distribution prédite Q :

$$
H(P,Q)=
-\sum_i P(i)\ln Q(i)
$$

$$
D_{\mathrm{KL}}(P\|Q)=
\sum_iP(i)\ln\frac{P(i)}{Q(i)}
$$

Elles vérifient :

$$
H(P,Q)=H(P)+D_{\mathrm{KL}}(P\|Q)
$$

**Intuition :** l'entropie croisée pénalise une prédiction qui attribue peu de probabilité aux événements attendus. La KL mesure un écart orienté entre distributions.

**Exemple :** pour une cible certaine sur une classe, une probabilité prédite de 0,9 donne une perte de −ln0,9≈0,105. Avec 0,1, la perte atteint environ 2,303.

**Application :** entrainer un routeur ou contraindre un modèle adapté à rester proche d'une référence.

**Pièges :**

- La KL n'est pas symétrique.
- Si P(i)>0 et Q(i)=0, la divergence peut être infinie.
- Reproduire une distribution de référence ne prouve pas la vérité de ses réponses.
- Une cible biaisée transmet son biais à l'objectif.

---

## 35  REINFORCE : apprendre une politique, avec prudence

**Priorité : P2**

Pour un épisode de durée finie, avec objectif

$$
J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=0}^{T-1}r_t\right]
$$

**sans actualisation**, une forme du gradient de politique est :

$$
\nabla_\theta J(\theta)=
\mathbb{E}_{\tau\sim\pi_\theta}
\left[
\sum_t
\nabla_\theta\ln\pi_\theta(a_t\mid h_t)
\left(G_t-b(h_t)\right)
\right]
$$

- τ : trajectoire d'interaction ;

- Gₜ=∑ᵤ₌ₜᵀ⁻¹rᵤ : somme des récompenses futures à partir de t, sans actualisation ici ;

- b(hₜ) : baseline indépendante de l'action sélectionnée, conditionnellement à l'historique.

**Intuition :** augmenter la probabilité des actions associées à de meilleurs retours que prévu.

**Application :** optimiser une politique de recherche ou d'utilisation d'outils lorsque les récompenses sont fiables.

**Pièges :** variance élevée, crédit difficile à attribuer et **reward hacking**. Un agent peut améliorer le score sans améliorer le service : fermer rapidement les tickets, éviter les cas difficiles ou produire des réponses convaincantes mais fausses.

Une récompense ne remplace pas l'architecture de controle :

- règles d'autorisation ;
- tests exécutables ;
- sandbox ;
- validations humaines ;
- surveillance indépendante.

Avant un apprentissage par renforcement, vérifier qu'une politique simple et mesurable ne suffit pas.

---

## 36  Fil rouge : agent de support SaaS avec RAG et outils

**Priorité : P0**

Considérons trois conditions de réussite :

1. retrouver la bonne procédure : 0,97 ;
2. choisir la bonne action, sachant la procédure correcte : 0,95 ;
3. exécuter correctement, sachant les étapes précédentes correctes : 0,99.

$$
q=0{,}97\times0{,}95\times0{,}99
=0{,}912285
$$

Le taux global attendu vaut **91,23 %** dans ce modèle. Ici, les probabilités sont conditionnelles : aucune indépendance supplémentaire n'est nécessaire pour ce produit.

Avec le budget hypothétique de la diapositive 12 :

$$
c_{\text{tokens}}=0{,}024\,€
$$

Le ratio tokens par résolution correcte vaut :

$$
\frac{c_{\text{tokens}}}{q}
\approx0{,}0263\,€
$$

**Interprétation :** cout total des tokens de toutes les tentatives, rapporté au nombre de résolutions correctes.

**Piège :** ce n'est pas le cout d'une tâche rejouée jusqu'au succès. Les échecs, reprises et escalades doivent être inclus dans le cout moyen réel.

Si trois recherches prennent 2, 3 et 4 secondes en parallèle, puis la synthèse 1 seconde, la latence idéale est de 5 secondes.

---

## 37  Comparer deux architectures : le moins cher n'est pas toujours préférable

**Priorité : P0**

Pour un échantillon défini :

$$
\operatorname{CoûtParRésolutionCorrecte}=
\frac{\sum_i C_i}
{\sum_i \mathbf1(\text{résolution correcte}_i)}
$$

Pour de grands volumes représentatifs, ce ratio est approximativement c/q, où c est le cout moyen par demande et q le taux de résolution correcte.

**Exemple hypothétique :**

| Système | Cout moyen | Réussite | Cout par résolution correcte |
| ------- | ---------: | -------: | ---------------------------: |
| A       |    0,024 € |  91,23 % |                     0,0263 € |
| B       |    0,030 € |     97 % |                     0,0309 € |

A est moins cher selon ce ratio. Pourtant, si le contrat exige au moins 95 % de réussite, A est inadmissible.

**Application :** comparer des modèles, des stratégies RAG ou des workflows sous contraintes métier.

**Piège :** ces valeurs ne prouvent aucune optimalité. Il faut ajouter incertitude statistique, latence, incidents, confidentialité et cout humain. Une faible fréquence d'erreurs ne rend pas acceptable une catégorie d'erreurs interdite.

---

## 38  Exercice Python : calculer et vérifier les hypothèses

Le code suivant utilise uniquement la bibliothèque standard. Il vérifie quatre calculs du support.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cosine(x, y)`** — Cette fonction se comporte comme un géomètre méticuleux qui, avant de mesurer l'angle entre deux flèches, vérifie d'abord qu'elles vivent dans le même espace : elle reçoit deux vecteurs x et y, lève une `ValueError` « Dimensions incompatibles » si leurs longueurs diffèrent, puis calcule la norme de chacun comme la racine de la somme des carrés de ses composantes. Si l'une des deux normes est nulle, elle refuse de conclure et lève une seconde `ValueError`, car un vecteur nul n'a pas de direction ; sinon elle renvoie le produit scalaire divisé par le produit des normes, soit 0,707107 pour [1, 0] et [1, 1], deux flèches séparées de 45°, et `main` s'en sert pour vérifier la formule du cosinus de la synthèse.

**`token_cost(n_in, n_out, rate_in, rate_out)`** — Voici le caissier d'une plateforme de modèles, qui tient sa grille tarifaire au million de tokens : il reçoit le nombre de tokens lus en entrée, le nombre de tokens produits en sortie et les deux prix correspondants, multiplie chaque quantité par son tarif, additionne les deux montants et divise le total par un million pour ramener la facture à un seul appel. Il renvoie ce coût en euros sans rien vérifier d'autre : pour 8 000 tokens d'entrée à 2 € et 1 000 tokens de sortie à 8 €, la note s'élève à 0,024 €, montant que `main` divise ensuite par la fiabilité de la chaîne pour obtenir le coût par résolution correcte.

**`retry_stats(p, attempts)`** — Cette fonction raconte la persévérance d'un agent qui frappe plusieurs fois à la même porte : elle reçoit la probabilité p qu'un essai réussisse et le nombre maximal d'essais autorisés, et commence par jouer les gardiens en levant une `ValueError` « Paramètres invalides » si p n'est pas strictement positif et au plus égal à 1, ou si l'on accorde moins d'un essai. Elle calcule ensuite la probabilité de réussir au moins une fois, 1 − (1 − p) puissance le nombre d'essais, puis le nombre moyen d'essais réellement consommés, somme des (1 − p) puissance j pour j allant de 0 au nombre d'essais moins un, puisqu'un essai n'a lieu que si tous les précédents ont échoué. Elle renvoie ce couple, 0,992 et 1,24 pour p = 0,8 et trois essais, ce qui montre qu'une relance bien bornée fait grimper la réussite sans tripler la dépense.

**`main()`** — C'est le contrôleur qui passe en revue les quatre calculs du support, comme un inspecteur qui coche une liste : il calcule avec `prod` la fiabilité q d'une chaîne de trois étapes fiables à 0,97, 0,95 et 0,99, soit 0,912285, demande à `token_cost` le prix d'un appel, 0,024 €, puis imprime le cosinus, la réussite de la chaîne, le coût, le coût par résolution correcte, 0,026308 €, et le couple renvoyé par `retry_stats`. Chaque valeur est ensuite confrontée par un `assert` au résultat attendu, après quoi il vérifie qu'une probabilité nulle avec trois essais, une probabilité de 0,8 avec zéro essai et un vecteur nul sont bien refusés par une `ValueError`, en levant une `AssertionError` dans le cas contraire, et il n'annonce que toutes les vérifications sont passées qu'au bout de ce parcours.

```python
from math import sqrt, prod
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def cosine(x, y):
    if len(x) != len(y):
        raise ValueError("Dimensions incompatibles")
    nx = sqrt(sum(v * v for v in x))
    ny = sqrt(sum(v * v for v in y))
    if nx == 0 or ny == 0:
        raise ValueError("Cosinus indéfini pour un vecteur nul")
    return sum(a * b for a, b in zip(x, y)) / (nx * ny)

def token_cost(n_in, n_out, rate_in, rate_out):
    return (n_in * rate_in + n_out * rate_out) / 1_000_000

def retry_stats(p, attempts):
    if not 0 < p <= 1 or attempts < 1:
        raise ValueError("Paramètres invalides")
    success = 1 - (1 - p) ** attempts
    expected = sum((1 - p) ** j for j in range(attempts))
    return success, expected


def main() -> None:
    q = prod([0.97, 0.95, 0.99])
    cost = token_cost(8000, 1000, 2, 8)

    print(f"Cosinus : {cosine([1, 0], [1, 1]):.6f}")
    print(f"Réussite chaine : {q:.6f}")
    print(f"Cout tokens : {cost:.6f} €")
    print(f"Cout / résolution correcte : {cost / q:.6f} €")
    print("Retry :", tuple(round(x, 6)
                           for x in retry_stats(0.8, 3)))

    assert round(cosine([1, 0], [1, 1]), 6) == 0.707107
    assert round(q, 6) == 0.912285 and round(cost, 6) == 0.024
    assert round(cost / q, 6) == 0.026308
    assert tuple(round(x, 6) for x in retry_stats(0.8, 3)) == (0.992, 1.24)
    for invalide in ((0, 3), (0.8, 0)):
        try:
            retry_stats(*invalide)
        except ValueError:
            pass
        else:
            raise AssertionError("paramètres invalides acceptés")
    try:
        cosine([0, 0], [1, 1])
    except ValueError:
        pass
    else:
        raise AssertionError("vecteur nul accepté")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

**Résultats attendus :** cosinus 0,707107, réussite 0,912285, cout 0,024 €, ratio 0,026308 €, retries (0,992; 1,24).

**Complément : vérifier les formules ajoutées (12b, 15, 23, 27b, 28, 29b).**

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`agent_loop_tokens(n0, delta, turns)`** — Cette fonction suit un agent qui, à chaque tour de sa boucle, relit tout son historique, comme un conteur obligé de reprendre son récit depuis le début avant d'y ajouter un chapitre : elle reçoit le nombre n₀ de tokens du contexte initial, l'accroissement Δ de l'historique à chaque tour et le nombre T de tours. Elle additionne T fois le contexte de départ et la somme des surplus accumulés, Δ × T × (T − 1) / 2, calculée en division entière, puis renvoie le nombre total de tokens lus : 97 500 pour 10 tours et 345 000 pour 20 tours avec n₀ = 3 000 et Δ = 1 500, si bien que doubler le nombre de tours multiplie la facture par environ 3,54 et non par 2, ce que `main` imprime pour rendre visible la croissance quadratique.

**`mrr(first_ranks)`** — On peut l'imaginer en examinateur qui note chaque question d'après la place où la première bonne réponse est apparue : elle reçoit la liste des rangs du premier document pertinent, un par question, avec `None` lorsqu'aucun pertinent n'a été trouvé. Pour chaque rang elle prend son inverse, 1 pour un premier rang, un tiers pour un troisième, et 0 quand le rang manque, puis divise la somme par le nombre de questions et renvoie ce rang réciproque moyen, environ 0,444 pour la liste [1, 3, None], soit (1 + 1/3 + 0) / 3 ; elle sert à vérifier la formule du MRR de la synthèse, et une liste vide la ferait échouer sur une division par zéro.

**`pass_at_k(n, c, k)`** — Cette fonction se place du côté d'un correcteur indulgent qui accepte la copie dès qu'une seule des k tentatives tirées au hasard est juste : elle reçoit le nombre n de générations disponibles, le nombre c de générations correctes parmi elles et le nombre k de tentatives tirées sans remise. Elle calcule avec `comb` la probabilité que les k tirages tombent tous parmi les n − c générations fausses, C(n − c, k) / C(n, k), puis renvoie son complément : pour n = 10, c = 7 et k = 3, il n'existe qu'une façon sur 120 de ne tirer que des échecs, d'où 119/120, environ 0,992, valeur que `main` contrôle à 10⁻¹² près.

**`pass_hat_k(n, c, k)`** — C'est la jumelle sévère de la précédente, un correcteur qui n'accepte le travail que si les k tentatives tirées sont toutes justes, comme un client qui exige que chaque relance d'un agent réussisse : elle reçoit les mêmes n, c et k et renvoie directement le rapport C(c, k) / C(n, k), nombre de façons de ne tirer que des générations correctes divisé par le nombre total de tirages possibles. Avec 7 générations correctes sur 10 et k = 3, cela donne 35/120, environ 0,292, si bien que `main` peut afficher côte à côte l'optimisme de pass@3, 0,992, et l'exigence de pass^3, 0,292, calculés sur les mêmes données.

**`majority(p, n)`** — Cette fonction convoque un petit jury de n votants indépendants, chacun juste avec la probabilité p, et se demande quelle chance a la majorité de pencher du bon côté : elle reçoit p et le nombre n de voix, supposé impair, puis additionne, pour chaque nombre k de bonnes voix allant de (n + 1) / 2 jusqu'à n, la probabilité binomiale C(n, k) × pᵏ × (1 − p)ⁿ⁻ᵏ. Elle renvoie cette probabilité de vote majoritaire correct, 0,784 pour trois votants justes à 70 % et 0,837 pour cinq, ce qui permet à `main` de montrer qu'agrandir le jury améliore le verdict tant que les voix restent indépendantes.

**`mcnemar(b, c)`** — Voici l'arbitre qui compare deux versions d'un agent en ne regardant que les tâches sur lesquelles elles se contredisent : il reçoit b, le nombre de tâches que seule la première version réussit, et c, le nombre de tâches que seule la seconde réussit, puis calcule la statistique de McNemar avec correction de continuité, (|b − c| − 1)² / (b + c). Il renvoie ce nombre, 5,625 pour 12 et 28 désaccords, soit 15² / 40, que l'on compare ensuite à la loi du khi-deux à un degré de liberté ; la fonction ne protège pas le cas où b + c vaut 0, qui provoquerait une division par zéro.

**`kappa(p_o, p_h, p_j)`** — Cette fonction joue le médiateur entre un annotateur humain et un LLM juge qui classent les mêmes réponses en acceptées ou refusées : elle reçoit l'accord observé `p_o`, la proportion `p_h` de réponses que l'humain accepte et la proportion `p_j` que le juge accepte. Elle calcule d'abord l'accord qu'on obtiendrait par pur hasard, `p_h * p_j + (1 - p_h) * (1 - p_j)`, puis renvoie le kappa de Cohen, (accord observé − accord du hasard) / (1 − accord du hasard), c'est-à-dire la part de l'accord qui dépasse la chance ; avec 0,85, 0,80 et 0,85, l'accord dû au hasard vaut 0,71 et le kappa environ 0,483, bien plus modeste que les 85 % d'accord brut ne le laissaient croire.

**`main()`** — Ce second chef d'orchestre fait défiler les formules ajoutées au support comme on accorde un à un les instruments avant le concert : il calcule les tokens d'une boucle de 10 puis de 20 tours avec `agent_loop_tokens` et exige 97 500 et 345 000, puis contrôle par des `assert` le MRR de [1, 3, None] à 10⁻⁶ près de 0,444444, pass@3 égal à 119/120 et pass^3 égal à 35/120, les votes majoritaires 0,784 et 0,837, la statistique de McNemar 5,625 et le kappa arrondi à 0,48. Il vérifie aussi que log 2 / log(1 / 0,995) s'arrondit à 138, nombre de pas au bout duquel un poids multiplié par 0,995 à chaque pas tombe de moitié, puis imprime chaque résultat, dont le rapport ×3,54 entre les deux boucles, et ne termine par le message de succès que si aucune assertion n'a échoué.

```python
from math import comb, log

def agent_loop_tokens(n0, delta, turns):
    return turns * n0 + delta * turns * (turns - 1) // 2

def mrr(first_ranks):
    return sum(1 / r if r else 0 for r in first_ranks) / len(first_ranks)

def pass_at_k(n, c, k):
    return 1 - comb(n - c, k) / comb(n, k)

def pass_hat_k(n, c, k):
    return comb(c, k) / comb(n, k)

def majority(p, n):
    return sum(comb(n, k) * p**k * (1 - p)**(n - k)
               for k in range((n + 1) // 2, n + 1))

def mcnemar(b, c):
    return (abs(b - c) - 1) ** 2 / (b + c)

def kappa(p_o, p_h, p_j):
    p_e = p_h * p_j + (1 - p_h) * (1 - p_j)
    return (p_o - p_e) / (1 - p_e)


def main() -> None:
    n10, n20 = agent_loop_tokens(3000, 1500, 10), agent_loop_tokens(3000, 1500, 20)
    assert (n10, n20) == (97_500, 345_000)
    assert abs(mrr([1, 3, None]) - 0.444444) < 1e-6
    assert abs(pass_at_k(10, 7, 3) - 119 / 120) < 1e-12
    assert abs(pass_hat_k(10, 7, 3) - 35 / 120) < 1e-12
    assert round(majority(0.7, 3), 3) == 0.784 and round(majority(0.7, 5), 3) == 0.837
    assert round(mcnemar(12, 28), 3) == 5.625
    assert round(kappa(0.85, 0.80, 0.85), 2) == 0.48
    assert round(log(2) / log(1 / 0.995)) == 138

    print(f"Tokens boucle 10 / 20 tours : {n10} / {n20} (x{n20 / n10:.2f})")
    print(f"MRR : {mrr([1, 3, None]):.3f}")
    print(f"pass@3 : {pass_at_k(10, 7, 3):.3f}   pass^3 : {pass_hat_k(10, 7, 3):.3f}")
    print(f"Vote 3 / 5 : {majority(0.7, 3):.3f} / {majority(0.7, 5):.3f}")
    print(f"McNemar : {mcnemar(12, 28):.3f}   kappa : {kappa(0.85, 0.80, 0.85):.3f}")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

**Sortie attendue :**

```text
Tokens boucle 10 / 20 tours : 97500 / 345000 (x3.54)
MRR : 0.444
pass@3 : 0.992   pass^3 : 0.292
Vote 3 / 5 : 0.784 / 0.837
McNemar : 5.625   kappa : 0.483
OK — toutes les vérifications sont passées.
```

**Travail demandé :** ajouter des tests pour les vecteurs nuls, les limites budgétaires et les erreurs déterministes. Puis reproduire ces calculs dans un service Java.

**Piège :** un calcul exact sur des hypothèses fausses donne une conclusion fausse avec beaucoup de décimales.

---

### Comment le code fonctionne

Le premier programme vérifie quatre calculs des diapositives. `cosine` refuse deux vecteurs de dimensions différentes, puis calcule les deux normes et refuse un vecteur nul, avant de renvoyer le produit scalaire divisé par le produit des normes : pour [1 ; 0] et [1 ; 1], l'angle est de 45° et le cosinus vaut 0,707107. `token_cost` calcule le coût d'un appel à partir de prix exprimés par million de tokens, d'où la division par un million : 8 000 tokens d'entrée à 2 € et 1 000 tokens de sortie à 8 € coûtent 0,024 €. La fiabilité d'une chaîne de trois étapes fiables à 97 %, 95 % et 99 % est leur produit, 0,912285, calculé avec `prod` ; et le coût par résolution correcte divise le coût d'un essai par cette fiabilité, parce qu'il faut en moyenne 1 / q essais pour obtenir une résolution juste. `retry_stats` renvoie deux nombres pour une probabilité p et un nombre d'essais : la probabilité de réussir au moins une fois, 1 − (1 − p) puissance n, et le nombre moyen d'essais réellement faits, la somme des (1 − p) puissance j (la formule des queues de l'étape 11), soit 0,992 et 1,24 pour p = 0,8 et trois essais. Les deux boucles `try` finales vérifient que les entrées invalides sont bien refusées.

Le second programme vérifie les formules ajoutées au support. `agent_loop_tokens` additionne les tokens relus à chaque tour d'une boucle d'agent dont l'historique grossit de Δ par tour : T n₀ + Δ T (T − 1) / 2, d'où le facteur 3,54 entre 10 et 20 tours au lieu de 2. `mrr` fait la moyenne des rangs réciproques, avec 0 pour une question sans pertinent ; `pass_at_k` et `pass_hat_k` sont les deux formules combinatoires de l'étape 13 bis ; `majority` additionne les probabilités binomiales d'avoir une majorité de bonnes réponses parmi n votes indépendants, ce qui montre qu'un vote à 5 voix fait mieux qu'un vote à 3 quand chaque voix est juste à 70 % ; `mcnemar` compare deux versions sur leurs désaccords, et `kappa` mesure l'accord entre un juge humain et un LLM juge au-delà de l'accord dû au hasard.

### Squelette algorithmique

```text
ALGORITHME CoûtParRésolutionCorrecte
ENTRÉES : fiabilités p₁ … pₙ des étapes, tokens d'entrée et de sortie, prix par million, p d'un essai, essais max
SORTIE  : coût par résolution correcte, et effet des relances

  q ← Π pᵢ                                            (fiabilité de la chaîne)
  coût ← (N_in × prix_in + N_out × prix_out) / 10⁶
  coût_par_succès ← coût / q
  succès_avec_relances ← 1 − (1 − p)^essais
  essais_moyens ← Σ_{j=0}^{essais−1} (1 − p)^j
  RETOURNER coût_par_succès, succès_avec_relances, essais_moyens

ALGORITHME VoteMajoritaire
ENTRÉES : p (justesse d'une voix), n votants (impair)
  RETOURNER Σ_{k = (n+1)/2}^{n} C(n, k) pᵏ (1 − p)^(n−k)
```

**Complexité.** Le premier algorithme est linéaire en nombre d'étapes et d'essais. Le vote majoritaire additionne au plus n / 2 + 1 termes binomiaux, chacun calculé en O(n). Les autres fonctions du second programme sont en O(1), sauf `mrr`, linéaire en nombre de questions.

**Du squelette au code.** `CoûtParRésolutionCorrecte` correspond à `prod`, `token_cost` et `retry_stats` dans le `main` du premier programme ; `VoteMajoritaire` correspond à `majority` dans le second.

## 39  Protocole d'évaluation : rendre les résultats reproductibles

**Priorité : P0**

Un protocole utile sépare :

- **entrainement**, si nécessaire ;
- **développement**, pour modifier prompts et paramètres ;
- **test**, conservé pour l'évaluation finale.

La séparation doit se faire par familles de tâches, clients ou périodes lorsque des doublons proches risquent de créer une fuite.

**Versionner :**

- jeu de données et annotations ;
- modèle et paramètres ;
- prompt système ;
- corpus et index ;
- outils et schémas ;
- règles d'autorisation ;
- code d'orchestration.

**Rapporter :**

- taux de réussite et intervalle ;
- cout total par tâche et par résolution ;
- latences médiane et p95 ;
- qualité du retrieval ;
- escalades et incidents ;
- résultats par catégorie.

**Application agentique :** savoir si une amélioration vient du modèle, du corpus ou d'un changement de trafic.

**Piège :** réutiliser continuellement le test pour choisir les versions le transforme en jeu de développement. En production, surveiller les dérives et conserver des traces minimisées, expurgées de secrets et conformes aux règles de conservation.

---

## 40  Anti-patterns et checklist de mise en production

**Priorité : P0**

### Anti-patterns fréquents

- Interpréter un cosinus comme une probabilité.
- Afficher « 95 % de confiance » sans calibration.
- Déclarer une version meilleure après dix exemples.
- Multiplier les agents sans mesurer la fiabilité globale.
- Réessayer une écriture sans idempotence.
- Mesurer uniquement les couts de tokens.
- Confondre présence d'une citation et preuve.
- Confier les permissions au prompt.
- Optimiser la moyenne en ignorant les incidents extrêmes.

### Checklist opérationnelle

- [ ] Objectif et définition de réussite explicites.
- [ ] Baseline simple disponible.
- [ ] Jeu de test représentatif et versionné.
- [ ] Budgets tokens, cout, temps et nombre d'actions.
- [ ] Autorisations controlées coté serveur.
- [ ] Schémas d'outils et paramètres validés.
- [ ] Écritures idempotentes ou compensables.
- [ ] Arrêt et escalade définis.
- [ ] Intervalles d'incertitude rapportés.
- [ ] Observabilité et procédure de rollback.
- [ ] Données sensibles minimisées.

**Pourquoi cette liste compte :** les mathématiques deviennent utiles lorsqu'elles modifient une décision d'architecture, un seuil ou une procédure. Une formule isolée ne protège aucun utilisateur.

---

## 41 Plan d'apprentissage sur quatre semaines

### Semaine 1 Fondations P0

Étudier vecteurs, probabilités conditionnelles, espérance et cout.

**Exercice :** construire un calculateur Java de budgets et de couts. Reproduire l'exemple de Bayes puis modifier la prévalence.

**Livrable :** tests unitaires et tableau d'hypothèses.

### Semaine 2  RAG mesurable

Comparer BM25, embeddings et recherche hybride. Annoter des requêtes représentatives.

**Exercice :** mesurer Precision@5, Recall@5, MRR et NDCG@5 ; tester plusieurs segmentations documentaires, avec et sans MMR.

**Livrable :** rapport de retrieval distinct du rapport de réponse.

### Semaine 3  Fiabilité et exploitation

Ajouter timeouts, retries controlés avec backoff et jitter, idempotence, budgets de tours et de tokens (contexte cumulé), cache de prompt et traces.

**Exercice :** injecter des pannes, une surcharge et un outil renvoyant un résultat ambigu.

**Livrable :** tableau de bord cout, latence et erreurs.

### Semaine 4  Évaluation et optimisation P1

Calculer Wilson, mesurer pass^k sur des tâches rejouées, réaliser une comparaison appariée (McNemar), valider le juge LLM par son kappa et examiner la calibration des scores de confiance (ECE).

**Livrable :** décision documentée de mise en production.

**P2 ensuite, si justifié :** fine-tuning ou apprentissage d'une politique uniquement lorsqu'un problème mesuré résiste aux approches plus simples.

---

## 42 Fiche mémo : vingt-deux équations à mobiliser en production

Les formules détaillées figurent dans les diapositives précédentes. Ce tableau indique **quand les utiliser** et **quoi vérifier avant de leur faire confiance**.

| # | Équation ou famille | Décision éclairée | Hypothèse ou vigilance |
| ---: | -------------------------- | ----------------------------------------- | ------------------------------------------ |
| 1 | Cosinus | Quels passages rapprocher ? | Vecteurs non nuls ; score non probabiliste |
| 2 | Bayes | Quelle valeur donner à une alerte ? | Taux de base représentatif |
| 3 | Espérance | Quel cout moyen prévoir ? | Inclure les branches rares |
| 4 | Cout des tokens | Quel budget autoriser ? | Tarifs et catégories exacts |
| 5 | BM25 | Comment retrouver les termes précis ? | Tokenisation et corpus |
| 6 | RRF | Comment fusionner les moteurs ? | Rangs comparables, permissions |
| 7 | Precision@k | Combien de résultats utiles ? | Convention sur les résultats retournés |
| 8 | Recall@k | Quelles preuves manque-t-on ? | Pertinence annotée suffisamment complète |
| 9 | NDCG@k | Les meilleurs passages arrivent-ils tot ? | Barème de pertinence stable |
| 10 | Produit conditionnel | Quelle fiabilité globale ? | Ne pas inventer l'indépendance |
| 11 | Retry tronqué | Combien de reprises autoriser ? | Idempotence et dépendance des pannes |
| 12 | Chemin critique | Que paralléliser ? | Dépendances et contention |
| 13 | Wilson | Quelle incertitude sur la réussite ? | Échantillonnage approprié |
| 14 | Perte attendue et seuil | Quand escalader ? | Couts réalistes et score calibré |
| 15 | Cout / résolution correcte | Quelle architecture est rentable ? | Périmètre complet et qualité minimale |
| 16 | Contexte cumulé (12b) | Combien de tours autoriser ? | Taille réelle des résultats d'outils, cache |
| 17 | MRR (15) | Le premier bon passage arrive-t-il tot ? | Convention si aucun pertinent |
| 18 | Score mémoire (16b) | Quels souvenirs injecter ? | Composantes sur la même échelle |
| 19 | Backoff + jitter (24) | Quand relancer ? | Respecter `Retry-After` |
| 20 | pass^k (27b) | L'agent est-il constant ? | Essais réellement indépendants, n≥ k |
| 21 | McNemar (28) | B bat-il vraiment A ? | Mêmes tâches ; test exact si peu de paires |
| 22 | Kappa (29b) | Peut-on faire confiance au juge LLM ? | Annotation humaine de référence |

**Principe :** mémoriser d'abord le sens, les unités et les hypothèses. La forme algébrique seule est insuffisante.

---

## 43  Références pour approfondir

Ces références correspondent aux familles de notions présentées ; les résultats numériques du support sont des exemples pédagogiques, pas des résultats tirés de ces travaux.

### Modèles, information et décision

- **Vaswani et al.  *Attention Is All You Need*, 2017.**  
  Architecture Transformer et attention :  
  https://arxiv.org/abs/1706.03762

- **Sutton et Barto  *Reinforcement Learning: An Introduction*, 2e édition.**  
  MDP, Bellman, politiques et apprentissage par renforcement :  
  https://incompleteideas.net/book/the-book-2nd.html

- **Auer, Cesa-Bianchi et Fischer  *Finite-time Analysis of the Multiarmed Bandit Problem*, 2002.**  
  Analyse d'UCB1 :  
  https://doi.org/10.1023/A:1013689704352

### Recherche d'information

- **Manning, Raghavan et Schatze  *Introduction to Information Retrieval*, 2008.**  
  Recherche lexicale, classement et évaluation :  
  https://nlp.stanford.edu/IR-book/

### Exploitation et évaluation

- **Little  *A Proof for the Queuing Formula: L = λW*, 1961.**  
  https://doi.org/10.1287/opre.9.3.383

- **Wilson  *Probable Inference, the Law of Succession, and Statistical Inference*, 1927.**  
  https://doi.org/10.1080/01621459.1927.10502953

- **Brier  *Verification of Forecasts Expressed in Terms of Probability*, 1950.**  
  Référence historique du score de Brier.

- **Guo et al.  *On Calibration of Modern Neural Networks*, 2017.**  
  https://arxiv.org/abs/1706.04599

- **Cohen  *A Coefficient of Agreement for Nominal Scales*, 1960.**  
  Kappa de Cohen.

### Agents, génération et évaluation des LLM

- **Holtzman et al.  *The Curious Case of Neural Text Degeneration*, 2019.**  
  Échantillonnage top-p (nucleus) :  
  https://arxiv.org/abs/1904.09751

- **Carbonell et Goldstein  *The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries*, SIGIR 1998.**  
  Maximal Marginal Relevance.

- **Park et al.  *Generative Agents: Interactive Simulacra of Human Behavior*, 2023.**  
  Score de mémoire récence + importance + pertinence :  
  https://arxiv.org/abs/2304.03442

- **Chen et al.  *Evaluating Large Language Models Trained on Code*, 2021.**  
  Estimateur sans biais de pass@k :  
  https://arxiv.org/abs/2107.03374

- **Yao et al.  *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*, 2024.**  
  Métrique pass^k pour la constance des agents :  
  https://arxiv.org/abs/2406.12045

- **Zheng et al.  *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, 2023.**  
  Biais et accord des juges LLM :  
  https://arxiv.org/abs/2306.05685

---

## 44 Conclusion : ce qui distingue un excellent développeur d'agents

Un excellent développeur d'IA agentique ne se reconnait pas au nombre de formules qu'il récite, mais à la qualité des décisions qu'il prend.

Il sait :

- distinguer similarité, probabilité et vérité ;
- raisonner sur les dépendances et l'incertitude ;
- calculer un cout complet, pas seulement une facture de tokens ;
- mesurer une amélioration avec un protocole reproductible ;
- refuser les actions non autorisées indépendamment du modèle ;
- arrêter une boucle dont la valeur marginale devient négative ;
- reconnaitre les limites de ses estimations.

**L'architecture cible n'est pas nécessairement multi-agent.** Un workflow déterministe, un moteur de recherche solide et quelques appels de modèle bien controlés peuvent être plus fiables qu'une orchestration complexe.

### Règle de travail

> Une formule utile relie une observation à une décision vérifiable, avec des unités et des hypothèses explicites.

Construire une baseline, mesurer ses erreurs, choisir le principal facteur limitant, puis améliorer une dimension à la fois.

**Recommandation finale : mesurer un agent simple avant de le complexifier.**

---

## 45 Où le calcul est déroulé

Chaque écran ci-dessus pose une formule. Le pas à pas, avec les nombres et le sens de chaque ligne de code, est dans les étapes du parcours, chacune rangée dans le chapitre où elle se lit (voir `00-Parcours-de-Lecture.md`). La table qui les relie aux équations est à la fin de `79-Index-des-Equations.md`.