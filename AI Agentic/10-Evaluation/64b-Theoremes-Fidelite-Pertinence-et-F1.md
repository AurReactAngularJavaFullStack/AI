# Étape 64 bis — Métriques d'évaluation d'un LLM et d'un agent : Faithfulness, Answer Relevancy, Precision, Recall, F1 — Théorèmes et démonstrations

> Étape 64 bis du parcours · Précédent : [Exact Match](<64-Evaluation-Formule-Exact-Match.md>) · Suite : [Exemples de métriques](<65-Evaluation-Exemples-Cas-Usage.md>)

**Ce que contient ce fichier :** les métriques qui transforment « la réponse a l'air bonne » en un nombre qu'on peut mettre comme seuil dans une pipeline CI/CD. Fidélité au contexte (Faithfulness), pertinence de la réponse (Answer Relevancy), Precision, Recall, F1 et F-bêta, Context Precision, Tool Call F1. Pour chacune : rôle, symboles définis un par un, théorème démontré, calcul à la main, code qui vérifie.

**Prérequis :** le cosinus et Cauchy–Schwarz (étape 28 bis), Precision@k (étape 28 bis, §8).

---

## Introduction — pourquoi des nombres

Dans un projet comme StaffMind, un agent qui qualifie une demande d'onboarding RH semble correct lors d'un test manuel. Après quelques semaines de production, des utilisateurs signalent des délais de déclaration inventés ou des conditions fiscales omises. Sans métrique, impossible de savoir si le défaut vient du prompt, du retrieval ou du modèle. Chaque métrique ci-dessous isole une cause :

| Métrique | Question posée | Cause isolée |
| --- | --- | --- |
| Faithfulness | La réponse invente-t-elle ? | Le modèle (hallucination) |
| Answer Relevancy | La réponse parle-t-elle de la question ? | Le prompt ou le modèle |
| Context Precision | Les bons chunks sont-ils en tête ? | Le retriever |
| Tool Call F1 | Les bons outils ont-ils été appelés ? | La boucle d'agent |

Une fois mesurées, on pose des seuils dans la CI (GitLab CI, GitHub Actions) et on bloque un déploiement qui ferait baisser la qualité.

---

## 1. Faithfulness (fidélité au contexte)

### Rôle

Mesurer la part de la réponse qui est **appuyée par le contexte récupéré**. Une réponse peut être vraie dans le monde réel et pourtant infidèle : si le contexte ne la contient pas, le modèle l'a tirée de sa mémoire d'entraînement, et on ne peut pas la tracer jusqu'à une source.

### Formule

$$
\text{Faithfulness} = \frac{\lvert V \rvert}{\lvert S \rvert}
$$

### Définition de chaque élément

$$
S = \{ s_1, s_2, \dots, s_N \}
$$

**S** : l'ensemble des affirmations atomiques (claims) extraites de la réponse. Une affirmation atomique ne peut pas être coupée en deux affirmations vérifiables séparément. L'extraction est faite par un LLM ou à la main.

$$
V \subseteq S
$$

**V** : le sous-ensemble des affirmations que le contexte permet de déduire. ⊆ se lit « est inclus dans ». Le jugement est rendu par un LLM juge ou un humain.

$$
\lvert S \rvert = N, \qquad \lvert V \rvert
$$

**|S|, |V| (cardinal)** : le nombre d'affirmations, total et appuyées.

$$
\lvert S \rvert = 0
$$

**Cas indéfini** : une réponse vide ou un refus (« je ne sais pas ») ne contient aucune affirmation. Le score n'est pas défini. On le traite à part, il ne faut pas le compter comme 0 ni comme 1.

### Théorème — Bornes et monotonie

**(a)** 0 ≤ Faithfulness ≤ 1, et Faithfulness = 1 si et seulement si toutes les affirmations sont appuyées.

**(b)** Ajouter une affirmation appuyée ne fait jamais baisser le score. Ajouter une affirmation non appuyée ne le fait jamais monter.

Notons v = |V| et s = |S|, avec 0 ≤ v ≤ s et s ≥ 1.

$$
\frac{v + 1}{s + 1} \ \ge\ \frac{v}{s} \qquad\qquad \frac{v}{s + 1} \ \le\ \frac{v}{s}
$$

### Démonstration

(a) V ⊆ S donne 0 ≤ v ≤ s, on divise par s > 0. L'égalité v/s = 1 équivaut à v = s, donc V = S.

(b) Première inégalité : on multiplie en croix par s(s + 1) > 0, ce qui ne change pas le sens :

$$
(v+1)\,s - v\,(s+1) = s - v \ \ge\ 0
$$

C'est vrai puisque v ≤ s. Seconde inégalité : s + 1 > s et v ≥ 0, donc diviser v par un nombre plus grand donne un résultat plus petit ou égal. ∎

### Propriété à connaître — le score dépend du découpage

Le même texte, découpé différemment, change de score. « Le plafond est de 1 500 € et la franchise de 300 € » compté comme **une** affirmation fausse donne 0/1 = 0. Découpé en **deux** affirmations, il donne 1/2 = 0,5. Pour comparer deux versions d'un agent, il faut utiliser le même extracteur d'affirmations.

### Exemple 1 — assurance

**Contexte** : « Pour un choc sur parking, le plafond de garantie dommages matériels est de 1 500 €. La franchise standard est de 150 €. Aucune franchise ne s'applique si le véhicule est stationné et que le conducteur n'est pas présent. »

**Réponse** : « Le plafond de garantie pour un choc sur parking est de 1 500 € et la franchise est de 300 €. Aucune franchise ne s'applique. »

| # | Affirmation | Jugement |
| --- | --- | --- |
| 1 | Le plafond pour un choc sur parking est de 1 500 € | Appuyée |
| 2 | La franchise est de 300 € | Non appuyée (le contexte dit 150 €) |
| 3 | Aucune franchise ne s'applique | Non appuyée : le contexte pose deux conditions que la réponse supprime |

$$
\lvert S \rvert = 3, \qquad \lvert V \rvert = 1, \qquad \text{Faithfulness} = \frac{1}{3} \approx 0{,}333
$$

### Exemple 2 — RH (StaffMind)

**Contexte** : « Au Royaume-Uni, un salarié en période d'essai peut prendre des congés payés après 3 mois de service effectif, sous réserve d'accord de l'employeur. »

**Réponse** : « Au Royaume-Uni, un salarié en période d'essai peut prendre des congés payés immédiatement. »

| # | Affirmation | Jugement |
| --- | --- | --- |
| 1 | Un salarié en période d'essai au Royaume-Uni peut prendre des congés payés | Appuyée |
| 2 | Il peut les prendre immédiatement | Non appuyée (le contexte dit après 3 mois) |

$$
\text{Faithfulness} = \frac{1}{2} = 0{,}5
$$

---

## 2. Answer Relevancy (pertinence de la réponse)

### Rôle

Une réponse peut être parfaitement fidèle et ne pas répondre à la question (« Le plafond est de 1 500 € » quand on demande la franchise). Answer Relevancy le détecte sans réponse de référence : on demande à un LLM de deviner, à partir de la réponse seule, quelles questions elle traite. Si ces questions devinées ressemblent à la vraie question, la réponse est pertinente.

### Formule

$$
\text{AR} = \frac{1}{n} \sum_{i=1}^{n} \cos(\mathbf{e}_{g_i}, \mathbf{e}_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{\mathbf{e}_{g_i} \cdot \mathbf{e}_o}{\lVert \mathbf{e}_{g_i} \rVert \, \lVert \mathbf{e}_o \rVert}
$$

### Définition de chaque élément

$$
\mathbf{e}_o
$$

**e_o** : l'embedding de la question originale (o pour « original »).

$$
g_1, \dots, g_n
$$

**gᵢ** : les n questions générées par le LLM à partir de la réponse (g pour « générée »). En pratique n = 3 à 5.

$$
\mathbf{e}_{g_i}
$$

**e_gᵢ** : l'embedding de la question générée gᵢ, avec le même modèle d'embedding que e_o.

$$
\cos(\mathbf{e}_{g_i}, \mathbf{e}_o)
$$

**cos** : la similarité cosinus de l'étape 28 bis.

$$
\frac{1}{n}\sum_{i=1}^{n}
$$

**Moyenne** : on additionne les n cosinus et on divise par n.

### Théorème — Bornes et forme « centroïde »

**(a)** −1 ≤ AR ≤ 1.

**(b)** Notons ê le vecteur normalisé (e / ‖e‖) et c̄ le centroïde des questions générées normalisées. Alors :

$$
\bar{\mathbf{c}} = \frac{1}{n}\sum_{i=1}^{n} \hat{\mathbf{e}}_{g_i}, \qquad \text{AR} = \hat{\mathbf{e}}_o \cdot \bar{\mathbf{c}} \ \le\ \lVert \bar{\mathbf{c}} \rVert \ \le\ 1
$$

**c̄ (c barre)** : le « centre de gravité » des questions générées, une fois ramenées à la longueur 1.

### Rôle du théorème (b)

AR ne peut pas dépasser ‖c̄‖. Or ‖c̄‖ est proche de 1 seulement si les questions générées vont **toutes dans la même direction**. Une réponse qui part dans plusieurs sujets produit des questions dispersées, un centroïde court, donc un AR plafonné, même si l'une des questions colle parfaitement.

### Démonstration

(a) Chaque cosinus est dans [−1, 1] (Cauchy–Schwarz, étape 28 bis §4). Une moyenne de nombres compris entre −1 et 1 est entre −1 et 1.

(b) Par le théorème 6 de l'étape 28 bis, cos(eᵢ, e_o) = êᵢ · ê_o. Le produit scalaire est linéaire, on peut sortir la somme :

$$
\text{AR} = \frac{1}{n}\sum_{i=1}^{n} \hat{\mathbf{e}}_{g_i} \cdot \hat{\mathbf{e}}_o = \left(\frac{1}{n}\sum_{i=1}^{n} \hat{\mathbf{e}}_{g_i}\right) \cdot \hat{\mathbf{e}}_o = \bar{\mathbf{c}} \cdot \hat{\mathbf{e}}_o
$$

Par Cauchy–Schwarz et ‖ê_o‖ = 1 : c̄ · ê_o ≤ ‖c̄‖ · 1. Par l'inégalité triangulaire (la longueur d'une somme est au plus la somme des longueurs) :

$$
\lVert \bar{\mathbf{c}} \rVert = \frac{1}{n}\left\lVert \sum_{i=1}^{n} \hat{\mathbf{e}}_{g_i} \right\rVert \le \frac{1}{n}\sum_{i=1}^{n} \lVert \hat{\mathbf{e}}_{g_i} \rVert = \frac{1}{n} \cdot n = 1
$$

∎

### Démonstration numérique

Embeddings simplifiés en 2D :

$$
\mathbf{e}_o = [0{,}9;\ 0{,}1], \qquad \mathbf{e}_{g_1} = [0{,}85;\ 0{,}15], \qquad \mathbf{e}_{g_2} = [0{,}7;\ 0{,}4], \qquad \mathbf{e}_{g_3} = [0{,}2;\ 0{,}8]
$$

Norme de la question originale :

$$
\lVert \mathbf{e}_o \rVert = \sqrt{0{,}81 + 0{,}01} = \sqrt{0{,}82} \approx 0{,}90554
$$

Question générée 1 :

$$
\cos_1 = \frac{0{,}9 \times 0{,}85 + 0{,}1 \times 0{,}15}{0{,}90554 \times \sqrt{0{,}745}} = \frac{0{,}78}{0{,}90554 \times 0{,}86313} = \frac{0{,}78}{0{,}78161} \approx 0{,}99795
$$

Question générée 2 :

$$
\cos_2 = \frac{0{,}9 \times 0{,}7 + 0{,}1 \times 0{,}4}{0{,}90554 \times \sqrt{0{,}65}} = \frac{0{,}67}{0{,}90554 \times 0{,}80623} = \frac{0{,}67}{0{,}73007} \approx 0{,}91772
$$

Question générée 3 :

$$
\cos_3 = \frac{0{,}9 \times 0{,}2 + 0{,}1 \times 0{,}8}{0{,}90554 \times \sqrt{0{,}68}} = \frac{0{,}26}{0{,}90554 \times 0{,}82462} = \frac{0{,}26}{0{,}74673} \approx 0{,}34819
$$

Moyenne :

$$
\text{AR} = \frac{0{,}99795 + 0{,}91772 + 0{,}34819}{3} = \frac{2{,}26386}{3} \approx 0{,}75462
$$

**Correction par rapport à l'ancienne version de ce fichier** : elle donnait 0,999 ; 0,89 ; 0,34 et une moyenne de 0,743. Les valeurs justes sont 0,998 ; 0,918 ; 0,348 et 0,755. Le code du §6 le vérifie.

Lecture : la question générée 3 part vers un autre sujet. Elle tire le score vers le bas à elle seule. C'est le signe d'une réponse qui contient un passage hors sujet.

---

## 3. Precision, Recall, F1

### Rôle

Ces trois taux comparent ce que le système a produit à ce qu'il aurait dû produire : des appels d'outils, des entités extraites, des chunks récupérés, des alertes de garde-fou. Context Precision et Tool Call F1 (plus bas) en sont des cas particuliers.

### Formules

$$
\text{P} = \frac{TP}{TP + FP}, \qquad \text{R} = \frac{TP}{TP + FN}, \qquad F_1 = 2 \cdot \frac{\text{P} \cdot \text{R}}{\text{P} + \text{R}}
$$

### Définition de chaque élément

$$
TP
$$

**TP (vrais positifs)** : les éléments produits **et** attendus. Ce que le système a bien fait.

$$
FP
$$

**FP (faux positifs)** : les éléments produits mais **pas** attendus. Le bruit, les appels inutiles, les fausses alertes.

$$
FN
$$

**FN (faux négatifs)** : les éléments attendus mais **pas** produits. Les oublis.

$$
TN
$$

**TN (vrais négatifs)** : ce qui n'était pas attendu et n'a pas été produit. Il n'apparaît dans aucune des trois formules. C'est voulu : pour un agent qui a des centaines d'outils, les TN sont énormes et sans intérêt.

$$
\text{P} \in [0, 1]
$$

**P (Precision)** : parmi ce que le système a produit, la part qui était juste.

$$
\text{R} \in [0, 1]
$$

**R (Recall, rappel)** : parmi ce qui était attendu, la part que le système a trouvée.

$$
F_1 \in [0, 1]
$$

**F₁** : la moyenne harmonique de P et R. Elle n'est élevée que si les deux le sont.

### Théorème 1 — Forme par les comptes

$$
F_1 = \frac{2\,TP}{2\,TP + FP + FN}
$$

### Démonstration

On remplace P et R par leurs définitions. Numérateur :

$$
2\,\text{P}\,\text{R} = \frac{2\,TP^2}{(TP+FP)(TP+FN)}
$$

Dénominateur, au même dénominateur commun :

$$
\text{P} + \text{R} = \frac{TP\,(TP+FN) + TP\,(TP+FP)}{(TP+FP)(TP+FN)} = \frac{TP\,(2\,TP + FP + FN)}{(TP+FP)(TP+FN)}
$$

Le quotient fait disparaître le dénominateur commun et un facteur TP :

$$
F_1 = \frac{2\,TP^2}{TP\,(2\,TP + FP + FN)} = \frac{2\,TP}{2\,TP + FP + FN}
$$

∎ Cette forme est plus sûre dans le code : elle reste définie quand P et R sont tous deux nuls (TP = 0 et FP + FN > 0 donnent F₁ = 0).

### Théorème 2 — F₁ est encadrée et punit le déséquilibre

$$
\min(\text{P}, \text{R}) \ \le\ F_1 \ \le\ \max(\text{P}, \text{R}), \qquad F_1 \ \le\ \frac{\text{P} + \text{R}}{2}
$$

avec égalité dans la dernière si et seulement si P = R.

### Démonstration

Supposons P ≤ R (l'autre cas est symétrique) et P + R > 0. Minoration : remplacer P par R au dénominateur l'agrandit, donc la fraction diminue :

$$
F_1 = \frac{2\,\text{P}\,\text{R}}{\text{P} + \text{R}} \ \ge\ \frac{2\,\text{P}\,\text{R}}{2\,\text{R}} = \text{P}
$$

Majoration : remplacer R par P au dénominateur le diminue :

$$
F_1 \ \le\ \frac{2\,\text{P}\,\text{R}}{2\,\text{P}} = \text{R}
$$

Comparaison avec la moyenne arithmétique : on calcule la différence.

$$
\frac{\text{P} + \text{R}}{2} - \frac{2\,\text{P}\,\text{R}}{\text{P} + \text{R}} = \frac{(\text{P} + \text{R})^2 - 4\,\text{P}\,\text{R}}{2\,(\text{P} + \text{R})} = \frac{(\text{P} - \text{R})^2}{2\,(\text{P} + \text{R})} \ \ge\ 0
$$

Un carré est positif, nul seulement si P = R. ∎

### Pourquoi la moyenne harmonique

Un agent qui appelle un seul outil, le bon, sur cent attendus a P = 1 et R = 0,01. La moyenne arithmétique lui donne 0,505, ce qui ressemble à une note moyenne. F₁ lui donne :

$$
F_1 = \frac{2 \times 1 \times 0{,}01}{1 + 0{,}01} \approx 0{,}0198
$$

Le théorème 2 explique ce résultat : F₁ reste proche du plus petit des deux taux.

### Généralisation — F-bêta

$$
F_\beta = \frac{(1 + \beta^2)\,\text{P}\,\text{R}}{\beta^2\,\text{P} + \text{R}}
$$

**β (bêta)** : le nombre de fois que le rappel compte plus que la précision. β = 1 redonne F₁. β = 2 : un oubli coûte plus qu'un appel en trop (garde-fou, détection de fraude). β = 0,5 : un appel en trop coûte plus qu'un oubli (outil qui envoie un e-mail ou un paiement).

### Exemple — appels d'outils

Attendus : `get_policy(country="UK")`, `check_eligibility()`.
Réels : `get_policy(country="UK")`, `get_policy(country="FR")`, `check_eligibility()`.

$$
TP = 2, \qquad FP = 1 \ (\texttt{get\_policy FR}), \qquad FN = 0
$$

$$
\text{P} = \frac{2}{3} \approx 0{,}667, \qquad \text{R} = \frac{2}{2} = 1, \qquad F_1 = \frac{2 \times 2}{2 \times 2 + 1 + 0} = \frac{4}{5} = 0{,}8
$$

Vérification du théorème 2 : 0,667 ≤ 0,8 ≤ 1, et 0,8 < (0,667 + 1)/2 ≈ 0,833.

Avec β = 2 :

$$
F_2 = \frac{5 \times \frac{2}{3} \times 1}{4 \times \frac{2}{3} + 1} = \frac{10/3}{11/3} = \frac{10}{11} \approx 0{,}909
$$

F₂ est plus indulgent que F₁ ici, parce que l'erreur est un appel en trop et pas un oubli.

---

## 4. Context Precision

### Rôle

Le LLM lit le contexte de haut en bas, et les chunks du début pèsent plus (étape 32 bis : le budget d'attention se partage). Context Precision vérifie que les chunks utiles sont **en tête** du contexte injecté, pas seulement présents.

### Formule

$$
\text{CP@}K = \frac{\displaystyle\sum_{k=1}^{K} \text{Precision@}k \cdot v_k}{\displaystyle\sum_{k=1}^{K} v_k}
$$

### Définition de chaque élément

$$
K
$$

**K** : le nombre de chunks injectés dans le prompt.

$$
v_k \in \{0, 1\}
$$

**v_k** : vaut 1 si le chunk au rang k est pertinent, 0 sinon (jugé par un LLM ou à la main).

$$
\text{Precision@}k = \frac{1}{k}\sum_{j=1}^{k} v_j
$$

**Precision@k** : la part de chunks pertinents parmi les k premiers (étape 28 bis, §8).

$$
\text{Precision@}k \cdot v_k
$$

**Le produit** : on ne compte Precision@k qu'aux rangs où se trouve un chunk pertinent. Un chunk inutile ne rapporte rien directement, mais il fait baisser la Precision@k de tous les chunks pertinents placés après lui.

$$
\sum_{k=1}^{K} v_k
$$

**Le dénominateur** : le nombre de chunks pertinents dans les K premiers. Si ce nombre vaut 0, la métrique n'est pas définie.

### Théorème — CP = 1 si et seulement si tous les pertinents sont devant

$$
\text{CP@}K = 1 \iff \text{aucun chunk non pertinent n'est placé avant un chunk pertinent}
$$

### Démonstration

Notons r le nombre de chunks pertinents. CP = 1 équivaut à une somme égale à r, c'est-à-dire, puisque chaque Precision@k ≤ 1, à Precision@k = 1 pour **chaque** rang k où v_k = 1.

(⇐) Si les r pertinents occupent les rangs 1 à r, alors pour chaque k ≤ r les k premiers sont tous pertinents, donc Precision@k = 1. La somme vaut r, CP = 1.

(⇒) Supposons qu'un chunk non pertinent au rang j précède un chunk pertinent au rang k > j. Parmi les k premiers, au moins un (celui du rang j) n'est pas pertinent, donc Precision@k ≤ (k − 1)/k < 1. Ce terme compte dans la somme (v_k = 1), donc la somme est < r et CP < 1. ∎

### Exemple

Quatre chunks injectés, pertinence v = [1, 0, 1, 1] :

$$
\text{Precision@}1 = 1, \quad \text{Precision@}2 = \tfrac{1}{2}, \quad \text{Precision@}3 = \tfrac{2}{3}, \quad \text{Precision@}4 = \tfrac{3}{4}
$$

$$
\text{CP@}4 = \frac{1 \times 1 + \tfrac{1}{2} \times 0 + \tfrac{2}{3} \times 1 + \tfrac{3}{4} \times 1}{3} = \frac{1 + 0{,}6667 + 0{,}75}{3} \approx 0{,}8056
$$

En remontant le chunk inutile en dernière position, v = [1, 1, 1, 0] et CP@4 = 1. Même contenu, meilleur ordre : c'est ce que fait un reranker.

---

## 5. Tool Call F1

### Rôle

Évaluer la boucle d'agent sur les **actions** et non sur le texte. Un agent peut écrire une réponse parfaite après avoir appelé un outil interdit ou oublié une vérification.

### Formule

$$
\text{Tool Call F}_1 = \frac{2\,\lvert C_{\text{réel}} \cap C_{\text{attendu}} \rvert}{\lvert C_{\text{réel}} \rvert + \lvert C_{\text{attendu}} \rvert}
$$

### Définition de chaque élément

$$
C_{\text{attendu}}
$$

**C_attendu** : le multi-ensemble des appels attendus. Un appel est le couple (nom de l'outil, arguments normalisés). Un multi-ensemble peut contenir deux fois le même appel : appeler deux fois `send_email` quand une seule était attendue doit compter un FP.

$$
C_{\text{réel}}
$$

**C_réel** : le multi-ensemble des appels effectivement faits par l'agent.

$$
\lvert C_{\text{réel}} \cap C_{\text{attendu}} \rvert = TP
$$

**L'intersection** : les appels présents des deux côtés, en comptant les répétitions au plus petit nombre. Ce sont les TP.

### Théorème — c'est exactement F₁

$$
\lvert C_{\text{réel}} \rvert = TP + FP, \qquad \lvert C_{\text{attendu}} \rvert = TP + FN \quad\Longrightarrow\quad \frac{2\,TP}{(TP+FP) + (TP+FN)} = F_1
$$

### Démonstration

Chaque appel réel est soit attendu (TP), soit en trop (FP), d'où la première égalité. Chaque appel attendu est soit fait (TP), soit oublié (FN), d'où la seconde. On additionne et on reconnaît la forme du théorème 1 du §3. ∎

Sur l'exemple du §3 : |C_réel| = 3, |C_attendu| = 2, intersection = 2, donc Tool Call F₁ = 4/5 = 0,8.

---

## 6. Code — tout vérifier

Bibliothèque standard uniquement. Chaque `assert` reprend un nombre de ce fichier.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`faithfulness(claims, is_supported)`** — Cette fonction est le vérificateur de faits qui relit la réponse affirmation par affirmation, le contexte ouvert à côté : elle reçoit la liste des affirmations extraites de la réponse et une fonction `is_supported` qui joue le juge, renvoie `None` si la liste est vide, parce qu'un refus ou une réponse vide n'a pas de fidélité définie, et sinon le nombre d'affirmations appuyées divisé par le nombre total. Sur l'exemple d'assurance, seule l'affirmation sur le plafond de 1 500 est soutenue, d'où 1/3 ; sur l'exemple des congés, une affirmation sur deux, d'où 0,5 ; `main` vérifie aussi, sur une grille de comptes, qu'ajouter une affirmation soutenue ne fait jamais baisser le score.

**`cosine(a, b)`** — Celle-ci est le rapporteur qui mesure l'angle entre deux flèches de sens : elle reçoit deux vecteurs, calcule leur produit scalaire et le divise par le produit de leurs normes, puis renvoie ce cosinus. Contrairement à la fonction canonique du parcours, elle ne vérifie ni que les deux vecteurs ont la même dimension, `zip` tronquant alors en silence, ni qu'aucun n'est nul, ce qui ferait lever une division par zéro. Entre la question d'origine (0,9 ; 0,1) et les trois questions générées, elle donne 0,99795, 0,91772 et 0,34819, les trois termes de l'Answer Relevancy.

**`normalize(a)`** — Cette fonction est le cartographe qui ne garde d'un vecteur que sa direction : elle reçoit un vecteur, calcule sa norme euclidienne et renvoie la liste de ses coordonnées divisées par cette norme, un vecteur de longueur 1, sans aucune garde, si bien qu'un vecteur nul ferait lever une division par zéro. `main` l'utilise pour la forme centroïde du théorème : il normalise chaque question générée, en fait la moyenne coordonnée par coordonnée, puis vérifie que le produit scalaire de la question d'origine normalisée avec ce centroïde redonne exactement l'Answer Relevancy, et que celle-ci ne dépasse pas la norme du centroïde.

**`answer_relevancy(e_o, generated)`** — Celle-ci est l'examinatrice qui fait reconstituer la question à partir de la seule réponse, puis compare chaque reconstitution à l'original : elle reçoit le vecteur de la question d'origine et la liste des vecteurs des questions générées, lève une `ValueError` s'il n'y en a aucune, et sinon renvoie la moyenne des cosinus entre chaque question générée et la question d'origine, calculés par `cosine`. Sur l'exemple, les trois cosinus donnent une moyenne de 0,75462 ; la troisième question, à 0,34819, est celle qui montre qu'une partie de la réponse s'éloigne du sujet.

**`precision_recall_f1(tp, fp, fn)`** — Cette fonction est le comptable qui tire trois ratios des mêmes comptes : elle reçoit les vrais positifs, les faux positifs et les faux négatifs, calcule la précision TP ÷ (TP + FP) et le rappel TP ÷ (TP + FN), puis le F1 sous la forme 2TP ÷ (2TP + FP + FN) démontrée au théorème 1, et remplace par 0 chaque taux dont le dénominateur est nul, là où d'autres fichiers du parcours renvoient `None`. Elle renvoie le triplet (précision, rappel, F1) : 2/3, 1 et 0,8 pour deux appels justes et un en trop, et `main` vérifie que ce F1 égale la moyenne harmonique et reste encadré par le plus petit et le plus grand des deux taux.

**`f_beta(p, r, beta)`** — Celle-ci est la balance réglable qui décide combien le rappel compte face à la précision : elle reçoit une précision, un rappel et β, calcule le dénominateur β²P + R, et renvoie (1 + β²)PR divisé par ce dénominateur, ou 0 si celui-ci est nul, sans vérifier que β est positif. Avec P = 2/3 et R = 1, elle donne 10/11, soit 0,909, pour β = 2, et redonne exactement le F1 de 0,8 pour β = 1, ce que `main` vérifie par deux `assert` ; plus β grandit, plus le score se rapproche du rappel.

**`context_precision(v)`** — Cette fonction est la critique qui juge un classement de passages à l'endroit où se trouvent les bons : elle reçoit la liste des pertinences 0 ou 1, rang par rang, lève une `ValueError` si aucun passage n'est pertinent, puis parcourt les rangs en comptant les pertinents déjà vus et n'ajoute la précision au rang k que lorsque ce rang est pertinent, avant de diviser par le nombre de pertinents. Elle renvoie 0,8056 pour [1, 0, 1, 1], c'est-à-dire (1 + 2/3 + 3/4) ÷ 3, et exactement 1 après réordonnancement en [1, 1, 1, 0], où tous les bons passages sont en tête.

**`tool_call_f1(actual, expected)`** — Celle-ci est l'inventaire qui confronte les appels d'outils réellement faits à ceux qu'on attendait, en comptant les répétitions : elle reçoit les deux listes d'appels, chaque appel étant un couple (nom, argument), les transforme en `Counter`, prend leur intersection de multi-ensembles, qui garde pour chaque appel le plus petit des deux comptes, et renvoie deux fois cette intersection divisée par la somme des deux tailles. Elle donne 0,8 quand l'agent ajoute un appel `get_policy` pour FR aux deux appels attendus, et 2/3 quand il envoie deux fois `send_email` au lieu d'une ; deux listes vides feraient lever une division par zéro.

**`main()`** — C'est le chef d'orchestre qui vérifie, dans l'ordre du fichier, chaque nombre des cinq sections : les fidélités 1/3 et 1/2, le cas indéfini et la monotonie sur une grille de comptes, puis les trois cosinus et l'Answer Relevancy de 0,75462 avec sa forme centroïde. Il contrôle ensuite les taux 2/3, 1 et 0,8 de l'exemple des appels d'outils, l'encadrement du F1, le F1 de 0,0198 qu'obtiennent une précision de 1 et un rappel de 0,01, et le F2 de 10/11, puis la Context Precision 0,8056 et 1 après réordonnancement, le Tool Call F1 de 0,8 et le cas de l'appel répété, imprime les résultats et termine par le « OK ».

```python
import math
from collections import Counter


def faithfulness(claims, is_supported):
    if not claims:
        return None   # indéfini : à traiter à part, ni 0 ni 1
    return sum(1 for c in claims if is_supported(c)) / len(claims)


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def normalize(a):
    n = math.sqrt(sum(x * x for x in a))
    return [x / n for x in a]


def answer_relevancy(e_o, generated):
    if not generated:
        raise ValueError("Il faut au moins une question générée")
    return sum(cosine(g, e_o) for g in generated) / len(generated)


def precision_recall_f1(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
    return p, r, f1


def f_beta(p, r, beta):
    denom = beta ** 2 * p + r
    return (1 + beta ** 2) * p * r / denom if denom else 0.0


def context_precision(v):
    if sum(v) == 0:
        raise ValueError("Aucun chunk pertinent : CP non défini")
    total, hits = 0.0, 0
    for k, vk in enumerate(v, start=1):
        hits += vk
        total += (hits / k) * vk
    return total / sum(v)


def tool_call_f1(actual, expected):
    a, e = Counter(actual), Counter(expected)
    tp = sum((a & e).values())          # intersection de multi-ensembles
    return 2 * tp / (sum(a.values()) + sum(e.values()))


def main() -> None:
    # §1 Faithfulness
    claims = ["plafond 1500", "franchise 300", "aucune franchise"]
    assert math.isclose(faithfulness(claims, lambda c: c == "plafond 1500"), 1 / 3)
    assert faithfulness(["congés possibles", "immédiatement"], lambda c: c == "congés possibles") == 0.5
    assert faithfulness([], lambda c: True) is None
    # monotonie (théorème b)
    for v in range(0, 6):
        for s in range(max(v, 1), 6):
            assert (v + 1) / (s + 1) >= v / s
            assert v / (s + 1) <= v / s

    # §2 Answer Relevancy
    e_o = [0.9, 0.1]
    gen = [[0.85, 0.15], [0.7, 0.4], [0.2, 0.8]]
    cosines = [cosine(g, e_o) for g in gen]
    assert all(math.isclose(c, x, abs_tol=1e-5) for c, x in zip(cosines, [0.99795, 0.91772, 0.34819]))
    ar = answer_relevancy(e_o, gen)
    assert math.isclose(ar, 0.75462, abs_tol=1e-5)
    # forme centroïde (théorème b)
    c_bar = [sum(col) / len(gen) for col in zip(*[normalize(g) for g in gen])]
    assert math.isclose(ar, sum(x * y for x, y in zip(normalize(e_o), c_bar)))
    assert ar <= math.sqrt(sum(x * x for x in c_bar)) <= 1

    # §3 Precision / Recall / F1
    p, r, f1 = precision_recall_f1(2, 1, 0)
    assert math.isclose(p, 2 / 3) and r == 1.0 and math.isclose(f1, 0.8)
    assert math.isclose(f1, 2 * p * r / (p + r))                 # théorème 1
    assert min(p, r) <= f1 <= max(p, r) and f1 <= (p + r) / 2    # théorème 2
    assert math.isclose(2 * 1 * 0.01 / 1.01, 0.0198, abs_tol=1e-4)
    assert math.isclose(f_beta(p, r, 2), 10 / 11)
    assert math.isclose(f_beta(p, r, 1), f1)

    # §4 Context Precision
    assert math.isclose(context_precision([1, 0, 1, 1]), 0.8056, abs_tol=1e-4)
    assert context_precision([1, 1, 1, 0]) == 1.0

    # §5 Tool Call F1
    expected = [("get_policy", "UK"), ("check_eligibility", "")]
    actual = [("get_policy", "UK"), ("get_policy", "FR"), ("check_eligibility", "")]
    assert math.isclose(tool_call_f1(actual, expected), 0.8)
    # un appel répété en trop compte bien comme FP
    assert math.isclose(tool_call_f1([("send_email", "")] * 2, [("send_email", "")]), 2 / 3)

    print(f"Faithfulness (assurance) = {1/3:.3f}")
    print("cosinus AR :", [round(c, 5) for c in cosines], f"-> AR = {ar:.5f}")
    print(f"P = {p:.3f}, R = {r:.3f}, F1 = {f1:.3f}, F2 = {f_beta(p, r, 2):.3f}")
    print(f"Context Precision [1,0,1,1] = {context_precision([1, 0, 1, 1]):.4f}")
    print(f"Tool Call F1 = {tool_call_f1(actual, expected):.3f}")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
Faithfulness (assurance) = 0.333
cosinus AR : [0.99795, 0.91772, 0.34819] -> AR = 0.75462
P = 0.667, R = 1.000, F1 = 0.800, F2 = 0.909
Context Precision [1,0,1,1] = 0.8056
Tool Call F1 = 0.800
OK — toutes les vérifications sont passées.
```

---

### Déroulé, ligne par ligne

`faithfulness` reçoit la liste des affirmations extraites de la réponse et une fonction `is_supported` qui joue le rôle du juge. Elle renvoie `None` quand la liste est vide, parce qu'un refus ou une réponse vide n'a pas de fidélité définie, et sinon le nombre d'affirmations appuyées divisé par le nombre total. `cosine` et `normalize` sont les fonctions du fichier 28 bis ; `answer_relevancy` fait la moyenne des cosinus entre chaque question générée et la question originale, et lève une erreur s'il n'y a aucune question générée.

`precision_recall_f1` calcule les trois taux à partir des comptes, et calcule F1 par la forme 2 TP / (2 TP + FP + FN) démontrée au théorème 1, qui reste définie quand précision et rappel sont nuls. `f_beta` donne au rappel un poids β² fois plus grand que celui de la précision, comme aux étapes 50 et 56. `context_precision` parcourt les chunks dans l'ordre, tient le compte des pertinents vus jusqu'au rang k, et n'ajoute la précision au rang k que lorsque le chunk de ce rang est pertinent, avant de diviser par le nombre de pertinents. `tool_call_f1` transforme les deux listes d'appels en multi-ensembles avec `Counter`, et leur intersection `a & e` garde le minimum des répétitions de chaque appel, ce qui compte bien un appel répété en trop comme un faux positif.

Le programme principal vérifie, dans l'ordre du fichier : les deux fidélités (1/3 et 1/2) et le cas indéfini, la monotonie de la fidélité sur une grille de comptes, les trois cosinus et la moyenne 0,75462 d'Answer Relevancy ainsi que sa forme centroïde, l'exemple des appels d'outils (P = 2/3, R = 1, F1 = 0,8, F2 = 10/11) avec l'encadrement de F1, la Context Precision 0,8056 puis 1 après réordonnancement, et le Tool Call F1 de 0,8.

## Squelette algorithmique

```text
ALGORITHME ÉvaluerUneRéponse
ENTRÉES : réponse, contexte, question, appels d'outils réels et attendus, chunks avec leur pertinence
SORTIE  : Faithfulness, Answer Relevancy, Context Precision, Tool Call F1

  S ← affirmations atomiques de la réponse                         (extraction par un LLM)
  SI S vide ALORS Faithfulness ← indéfinie
  SINON Faithfulness ← #{s ∈ S : le juge trouve s dans le contexte} / |S|
  g₁ … g_n ← questions générées à partir de la réponse
  AR ← moyenne des cos(embedding(gᵢ), embedding(question))
  vus ← 0 ; somme ← 0
  POUR k DE 1 À K FAIRE
      SI le chunk k est pertinent ALORS vus ← vus + 1 ; somme ← somme + vus / k
  FIN POUR
  CP ← somme / vus                                                 (indéfinie si vus = 0)
  TP ← |réels ∩ attendus| (multi-ensembles)
  TC_F1 ← 2 TP / (|réels| + |attendus|)
  RETOURNER Faithfulness, AR, CP, TC_F1
```

**Complexité.** Faithfulness coûte un appel au juge par affirmation : O(|S|) appels, qui dominent le coût. Answer Relevancy coûte n générations de questions et n + 1 embeddings, puis O(n × d) pour les cosinus. Context Precision est une passe O(K). Tool Call F1 coûte O(|réels| + |attendus|) avec des compteurs.

**Du squelette au code.** `faithfulness`, `answer_relevancy`, `context_precision` et `tool_call_f1` sont, dans l'ordre, les quatre blocs de l'algorithme ; `precision_recall_f1` et `f_beta` donnent les taux dont Tool Call F1 est un cas particulier.

## 7. Barrière de déploiement (CI/CD)

Les métriques n'ont de valeur que si elles bloquent quelque chose. Une barrière typique sur un jeu de test fixe :

$$
\text{déployer} \iff \overline{\text{Faithfulness}} \ge \tau_F \ \ \wedge\ \ \overline{\text{AR}} \ge \tau_{AR} \ \ \wedge\ \ \overline{\text{Tool Call F}_1} \ge \tau_T
$$

**Barre au-dessus (moyenne)** : la moyenne de la métrique sur toutes les questions du jeu de test.

**τ (tau)** : un seuil, fixé une fois pour toutes par métrique, par exemple τ_F = 0,95.

**∧ (et logique)** : toutes les conditions doivent être vraies en même temps.

**⟺ (si et seulement si)** : on déploie quand les conditions sont réunies, et seulement dans ce cas.

## 8. Cas d'usage réels

- **VerifactureBTP** : Faithfulness d'une facture générée par rapport aux règles légales récupérées. Un score inférieur à 0,95 bloque la génération automatique et envoie la facture en relecture humaine.
- **Contexte bancaire (Banque de France)** : Faithfulness combinée à une métrique de non-divulgation d'informations sensibles. Tool Call F₀,₅ plutôt que F₁ pour les outils qui écrivent : un appel en trop y est plus grave qu'un oubli.
- **StaffMind RH** : Answer Relevancy sur les questions d'onboarding, pour détecter les réponses qui dérivent vers un autre pays ou un autre contrat.

## 9. Pièges

- **Compter un refus comme Faithfulness = 0 ou = 1.** Le score est indéfini. Mesurer le taux de refus à part.
- **Changer d'extracteur d'affirmations entre deux versions.** Le score dépend du découpage (§1).
- **Lire Answer Relevancy comme une mesure de vérité.** Une réponse fausse mais sur le bon sujet a un AR élevé. C'est Faithfulness qui détecte l'invention.
- **Utiliser des ensembles au lieu de multi-ensembles pour Tool Call F1.** Un appel répété en trop disparaît alors du calcul.

## 10. Exercice feuille blanche

1. Démontrer F₁ = 2TP / (2TP + FP + FN) à partir des définitions de P et R.
2. Démontrer min(P, R) ≤ F₁ ≤ (P + R)/2.
3. Montrer que AR = ê_o · c̄ et en déduire qu'une réponse qui traite deux sujets a un AR plafonné.
4. Pour v = [0, 1, 1, 0, 1], calculer Context Precision, puis trouver l'ordre qui la rend égale à 1.
