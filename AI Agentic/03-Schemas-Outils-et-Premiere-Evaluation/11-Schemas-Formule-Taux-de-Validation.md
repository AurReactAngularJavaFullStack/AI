# Étape 11 — Schémas — Taux de validation de schéma et boucle de réparation

> Étape 11 du parcours · Prérequis : [Conformité d'un prompt et intervalle de Wilson](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>) (étape 7) et [Schémas : définitions et validateur](<08-Schemas-Definitions-Fondamentaux.md>) (étape 8) · Précédent : [Applications par domaine](<10-Schemas-Applications-Domaines.md>) · Suite : [Outils : définitions](<12-Outils-Definitions-Fondamentaux.md>) — étape 12

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Product Engineers, Forward-Deployed Engineers  
**Nom du fichier :** 11-Schemas-Formule-Taux-de-Validation.md

---

## Définition

À l'étape 8, l'agent demande au modèle un JSON, le passe dans un validateur, et, si le validateur trouve des erreurs, renvoie la liste au modèle pour qu'il corrige. Il le fait au plus R fois, puis il escalade vers un humain. Ce fichier mesure cette boucle avec quatre nombres.

1. **Le taux de validation au premier passage, V₁** : la part des demandes dont le **premier** JSON produit est valide. C'est la qualité du couple prompt + schéma + modèle.
2. **Le taux de validation après réparation, V_R** : la part des demandes qui finissent avec un JSON valide après au plus R relances. C'est ce que voit le reste du système.
3. **Le taux d'escalade, 1 − V_R** : la part des demandes qui partent chez un humain. C'est une charge de travail, qu'on dimensionne.
4. **Le nombre moyen d'essais** : le coût, en appels et en tokens.

Le fichier démontre ensuite les formules annoncées à l'étape 8. Elles valent sous l'hypothèse que chaque essai réussit avec la même probabilité p, indépendamment des autres :

- la probabilité de succès en au plus R + 1 essais vaut 1 − (1 − p)^(R+1) ;
- le nombre moyen d'essais vaut (1 − (1 − p)^(R+1)) / p ;
- avec p = 0,9 et R = 2, cela donne 0,999 et 1,11 essai.

Puis il montre où l'hypothèse d'indépendance casse : les cas difficiles restent difficiles à chaque relance, et une partie des entrées ne sera **jamais** réparée par le modèle.

## Rôle dans un agent

Un JSON invalide arrête la chaîne : l'outil suivant ne peut pas être appelé, le calcul ne peut pas être fait. Ces mesures servent à :

- **choisir R**, le nombre de relances : assez pour atteindre la cible de fiabilité, pas plus, car chaque relance coûte un appel et des tokens ;
- **dimensionner l'équipe humaine** qui reçoit les escalades : 1 − V_R multiplié par le volume quotidien ;
- **trouver le champ qui casse** : le décompte des erreurs par champ dit quelle description du schéma réécrire, ou quelle normalisation faire en code avant la validation ;
- **détecter une dérive** : une mise à jour du modèle qui fait chuter V₁ se voit le jour même, avec son intervalle de Wilson ;
- **relier la fiabilité d'une étape à celle de l'agent** : l'étape 1 a montré que la fiabilité se multiplie le long des étapes, et la réparation est le levier qui fait remonter chaque facteur.

---

## Équations complètes

Taux mesurés sur N demandes :

$$
\hat{V}_1 = \frac{k_1}{N}, \qquad \hat{V}_R = \frac{k_{R+1}}{N}, \qquad \text{taux d'escalade} = 1 - \hat{V}_R
$$

Probabilité de succès en au plus R + 1 essais indépendants :

$$
P_{\text{succ}}(R) = 1 - (1 - p)^{R+1}
$$

Nombre moyen d'essais :

$$
\mathbb{E}[A] = \sum_{i=0}^{R} (1 - p)^i = \frac{1 - (1 - p)^{R+1}}{p} = \frac{P_{\text{succ}}(R)}{p}
$$

Gain apporté par une relance de plus :

$$
P_{\text{succ}}(R + 1) - P_{\text{succ}}(R) = p\,(1 - p)^{R+1}
$$

Nombre minimal de relances pour une cible c :

$$
R_{\min} = \left\lceil \frac{\ln(1 - c)}{\ln(1 - p)} \right\rceil - 1
$$

Premier essai et relances de fiabilités différentes :

$$
P_{\text{succ}}(R) = 1 - (1 - p_1)(1 - p_r)^R
$$

Fraction irréparable f :

$$
P_{\text{succ}}(R) = (1 - f)\left(1 - (1 - p)^{R+1}\right) \ \le\ 1 - f
$$

Coût moyen en tokens d'entrée :

$$
\mathbb{E}[T] = \sum_{i=0}^{R} (1 - p)^i \,(b + i\,d)
$$

Fiabilité de n sorties structurées qui doivent toutes être valides :

$$
P_{\text{agent}} = P_{\text{succ}}(R)^{\,n}
$$

---

## Décryptage des symboles

### Comptages

$$
N
$$

**N** : le nombre de demandes traitées (un jeu de test, ou une journée de production).

$$
k_i
$$

**kᵢ** : le nombre de demandes qui ont un JSON valide **au plus tard au i-ème essai**. k₁ compte les succès du premier coup, k₂ ceux du premier ou du deuxième essai, etc. Par construction k₁ ≤ k₂ ≤ … ≤ N.

$$
\hat{V}_1 = \frac{k_1}{N}
$$

**V̂₁ (V un chapeau)** : le taux de validation au premier passage, observé. Le chapeau signale une estimation, comme à l'étape 7.

$$
\hat{V}_R = \frac{k_{R+1}}{N}
$$

**V̂_R** : le taux de validation après R relances, donc après au plus R + 1 essais.

### Modèle de la boucle

$$
R \in \{0, 1, 2, \dots\}
$$

**R** : le nombre maximal de **relances**. Le nombre maximal d'**essais** vaut donc R + 1. R = 0 veut dire « pas de réparation ».

$$
p \in \ ]0, 1]
$$

**p** : la probabilité qu'un essai donne un JSON valide.

$$
q = 1 - p
$$

**q** : la probabilité qu'un essai échoue. On l'écrit souvent pour alléger les formules.

$$
A \in \{1, \dots, R + 1\}
$$

**A** : le nombre d'essais réellement faits pour une demande. C'est une variable aléatoire : 1 si le premier essai réussit, R + 1 si l'on va jusqu'au bout, que le dernier essai réussisse ou non.

$$
\mathbb{E}[A]
$$

**𝔼[A]** : l'espérance de A, le nombre moyen d'essais sur un grand nombre de demandes.

$$
P_{\text{succ}}(R)
$$

**P_succ(R)** : la probabilité qu'une demande finisse avec un JSON valide quand on autorise R relances.

$$
c \in \ ]0, 1[
$$

**c** : la fiabilité visée pour une demande, par exemple 0,9995.

$$
\lceil x \rceil
$$

**⌈x⌉ (partie entière supérieure)** : le plus petit entier ≥ x. ⌈3,3⌉ = 4, ⌈4⌉ = 4.

$$
\ln
$$

**ln** : le logarithme naturel. Il transforme une puissance en produit : ln(q^n) = n ln q. Pour 0 < q < 1, ln q est **négatif**.

### Au-delà de l'indépendance

$$
p_1
$$

**p₁** : la probabilité de succès du premier essai.

$$
p_r
$$

**p_r** : la probabilité de succès d'une relance, sachant que les essais d'avant ont échoué. En pratique p_r < p₁ : les demandes qui ont échoué une fois sont les plus difficiles.

$$
f \in [0, 1]
$$

**f** : la fraction **irréparable**, celle des demandes pour lesquelles aucun JSON valide ne peut sortir du modèle, quel que soit le nombre de relances. Exemples : une information absente de l'entrée, ou une date ambiguë que le modèle ne peut pas trancher.

### Coût

$$
b
$$

**b** : le nombre de tokens d'entrée du premier appel (prompt système, schéma, demande).

$$
d
$$

**d** : le nombre de tokens ajoutés à chaque relance : la réponse fautive précédente, plus la liste des erreurs avec leurs chemins. L'historique grossit, donc la relance i coûte b + (i − 1)d.

$$
\mathbb{E}[T]
$$

**𝔼[T]** : le nombre moyen de tokens d'entrée consommés par demande.

$$
n
$$

**n** : le nombre de sorties structurées qui doivent toutes être valides pour qu'une tâche aboutisse (lignes d'un fichier de salaires, étapes d'un agent).

---

## Démonstration

### 1. Le taux après réparation ne peut que monter avec R

La boucle s'arrête au premier JSON valide. Une demande validée en au plus r essais est donc validée en au plus r + 1 essais : l'ensemble des demandes validées avec r essais est inclus dans celui avec r + 1 essais. Le cardinal d'un sous-ensemble est plus petit ou égal :

$$
k_1 \ \le\ k_2 \ \le\ \cdots \ \le\ k_{R+1} \ \le\ N \qquad\Longrightarrow\qquad \hat{V}_1 \ \le\ \hat{V}_R \ \le\ 1
$$

∎ Si un tableau de bord affiche V̂_R < V̂₁, ce n'est pas le modèle qui se comporte bizarrement : c'est le calcul qui est faux, par exemple deux jeux de demandes différents.

### 2. La probabilité de succès en au plus R + 1 essais

On passe par le complément. La demande échoue au bout du compte si et seulement si **tous** les R + 1 essais échouent. Par indépendance, la probabilité d'une intersection d'événements indépendants est le produit des probabilités, comme pour la fiabilité composée de l'étape 1 :

$$
P(\text{échec final}) = P(E_1 \cap E_2 \cap \cdots \cap E_{R+1}) = \prod_{i=1}^{R+1} P(E_i) = q^{R+1}
$$

**Eᵢ** : l'événement « l'essai i échoue », de probabilité q. Donc :

$$
P_{\text{succ}}(R) = 1 - q^{R+1} = 1 - (1 - p)^{R+1}
$$

∎ Avec p = 0,9 et R = 2 : 1 − 0,1³ = 1 − 0,001 = 0,999. C'est le résultat annoncé à l'étape 8.

### 3. Le nombre moyen d'essais, par la formule des queues

**Lemme (somme des queues).** Pour une variable A à valeurs entières positives :

$$
\mathbb{E}[A] = \sum_{i \ge 0} P(A > i)
$$

Démonstration du lemme. On écrit chaque valeur a comme une somme de 1, puis la variable A elle-même :

$$
a = \sum_{i=0}^{a-1} 1, \qquad A = \sum_{i \ge 0} \mathbb{1}[A > i]
$$

où **𝟙[·] (indicatrice)** vaut 1 si la condition est vraie, 0 sinon. On prend l'espérance, qui est linéaire, et on utilise 𝔼[𝟙[X]] = P(X) :

$$
\mathbb{E}[A] = \sum_{i \ge 0} \mathbb{E}\big[\mathbb{1}[A > i]\big] = \sum_{i \ge 0} P(A > i)
$$

∎

**Application.** On fait plus de i essais si et seulement si les i premiers ont tous échoué, et il reste un essai autorisé, c'est-à-dire i ≤ R. Donc P(A > i) = qⁱ pour 0 ≤ i ≤ R (avec q⁰ = 1 : on fait toujours au moins un essai), et P(A > i) = 0 pour i > R, puisque A ≤ R + 1 :

$$
\mathbb{E}[A] = \sum_{i=0}^{R} q^i = 1 + q + q^2 + \cdots + q^R
$$

**Somme géométrique.** Notons G cette somme. On la multiplie par q, et presque tous les termes se retrouvent :

$$
G - qG = (1 + q + \cdots + q^R) - (q + q^2 + \cdots + q^{R+1}) = 1 - q^{R+1}
$$

Donc G(1 − q) = 1 − q^(R+1). Comme 1 − q = p > 0 :

$$
\mathbb{E}[A] = \frac{1 - q^{R+1}}{p} = \frac{P_{\text{succ}}(R)}{p}
$$

∎ Avec p = 0,9 et R = 2 : 1 + 0,1 + 0,01 = 1,11 essai, soit 0,999 / 0,9. Le coût moyen n'est que 11 % au-dessus d'un essai unique : la réparation est bon marché quand p est grand, parce que la plupart des demandes s'arrêtent au premier essai.

La formule 𝔼[A] = P_succ / p a une lecture simple. Sur un grand nombre de demandes, chaque essai réussit en proportion p. Le nombre de succès vaut donc p × (nombre total d'essais). Il vaut aussi P_succ × (nombre de demandes). En égalant les deux, on retrouve le nombre d'essais par demande.

### 4. Chaque relance rapporte dix fois moins que la précédente (si q = 0,1)

$$
P_{\text{succ}}(R + 1) - P_{\text{succ}}(R) = q^{R+1} - q^{R+2} = q^{R+1}(1 - q) = p\,q^{R+1}
$$

Le rapport entre deux gains successifs vaut p q^(R+2) / (p q^(R+1)) = q. ∎

| R | P_succ(R) | Gain de la relance R |
| --- | --- | --- |
| 0 | 0,9 | — |
| 1 | 0,99 | 0,09 |
| 2 | 0,999 | 0,009 |
| 3 | 0,9999 | 0,0009 |
| 4 | 0,99999 | 0,00009 |

Les rendements sont décroissants. La première relance compte beaucoup, la quatrième presque plus. C'est pourquoi l'étape 8 fixe R = 2.

### 5. Combien de relances pour une cible c

On veut 1 − q^(R+1) ≥ c, c'est-à-dire q^(R+1) ≤ 1 − c. Le logarithme est strictement croissant, il conserve le sens de l'inégalité :

$$
(R + 1)\ln q \ \le\ \ln(1 - c)
$$

On divise par ln q, qui est **négatif** puisque 0 < q < 1. Diviser par un négatif **inverse** le sens :

$$
R + 1 \ \ge\ \frac{\ln(1 - c)}{\ln q} \qquad\Longrightarrow\qquad R_{\min} = \left\lceil \frac{\ln(1 - c)}{\ln(1 - p)} \right\rceil - 1
$$

∎ (Si le résultat est négatif, R_min = 0 : le premier essai suffit.) Avec la cible c = 0,9995 :

| p par essai | ln(0,0005) / ln(1 − p) | R_min |
| --- | --- | --- |
| 0,9 | 7,601 / 2,303 = 3,30 | 3 |
| 0,7 | 7,601 / 1,204 = 6,31 | 6 |
| 0,5 | 7,601 / 0,693 = 10,97 | 10 |

Lecture : quand p baisse, le nombre de relances nécessaires explose. Améliorer p (description du champ, exemple dans le prompt, normalisation en code) vaut mieux qu'ajouter des relances.

### 6. Quand le premier essai et les relances n'ont pas la même fiabilité

Une relance n'est pas un nouveau tirage indépendant : le modèle voit sa réponse fautive et la liste des erreurs. Notons p₁ la fiabilité du premier essai et p_r celle d'une relance, sachant que tout ce qui précède a échoué. Par la règle de multiplication des probabilités conditionnelles (étape 1, point 1) :

$$
P(\text{tous échouent}) = P(E_1) \times P(E_2 \mid E_1) \times \cdots \times P(E_{R+1} \mid E_1 \cap \cdots \cap E_R) = (1 - p_1)(1 - p_r)^R
$$

D'où P_succ(R) = 1 − (1 − p₁)(1 − p_r)^R. ∎ Avec p₁ = p_r = p, on retrouve la formule du point 2.

**Estimer p_r à partir des comptages.** Parmi les N − k₁ demandes qui ont échoué au premier essai, k₂ − k₁ ont réussi à la première relance. La proportion observée vaut :

$$
\hat{p}_r^{(1)} = \frac{k_2 - k_1}{N - k_1}, \qquad \hat{p}_r^{(2)} = \frac{k_3 - k_2}{N - k_2}
$$

Si p̂_r^(2) est nettement plus bas que p̂_r^(1), les relances successives s'adressent à des cas de plus en plus durs. Le modèle « indépendant » est alors trop optimiste.

### 7. La fraction irréparable plafonne tout

Supposons qu'une fraction f des demandes ne puisse jamais être réparée (P_succ = 0 pour elles), et que les autres suivent le modèle indépendant. Par la formule des probabilités totales, qui découpe selon le type de demande :

$$
P_{\text{succ}}(R) = (1 - f)\left(1 - q^{R+1}\right) + f \times 0 = (1 - f)\left(1 - q^{R+1}\right)
$$

Comme 1 − q^(R+1) ≤ 1, on a P_succ(R) ≤ 1 − f pour tout R. Quand R → ∞, q^(R+1) → 0 et P_succ(R) → 1 − f. ∎

Conséquence d'ingénierie : si V̂_R plafonne quand on augmente R, le plafond mesure f. Ajouter des relances ne sert plus à rien. Il faut **changer l'entrée** : demander l'information manquante à l'utilisateur, normaliser en code, ou corriger le schéma.

### 8. Le coût moyen en tokens

L'essai i (numéroté à partir de 1) coûte b + (i − 1)d tokens d'entrée, et il a lieu si et seulement si A ≥ i. Le coût total s'écrit donc T = Σᵢ 𝟙[A ≥ i] (b + (i − 1)d). Par linéarité de l'espérance, avec P(A ≥ i) = P(A > i − 1) = q^(i−1) (point 3) :

$$
\mathbb{E}[T] = \sum_{i=1}^{R+1} q^{\,i-1}\left(b + (i - 1)\,d\right) = \sum_{i=0}^{R} q^{\,i}\left(b + i\,d\right)
$$

∎ Avec b = 1 200, d = 400, p = 0,9 et R = 2 :

$$
\mathbb{E}[T] = 1\,200 + 0{,}1 \times 1\,600 + 0{,}01 \times 2\,000 = 1\,200 + 160 + 20 = 1\,380
$$

La réparation coûte en moyenne 15 % de tokens en plus. Si p tombait à 0,5, on aurait 1 200 + 0,5 × 1 600 + 0,25 × 2 000 = 2 500 tokens, plus du double.

### 9. Composer : n sorties qui doivent toutes être valides

Si une tâche demande n sorties structurées indépendantes, toutes valides, la fiabilité se multiplie (étape 1) :

$$
P_{\text{agent}} = P_{\text{succ}}(R)^n
$$

Sans réparation, avec p = 0,9 et n = 5 : 0,9⁵ ≈ 0,5905. Avec R = 2 : 0,999⁵ ≈ 0,9950. La réparation est le levier « rendre chaque étape plus fiable » de l'étape 1, point 5, et son effet est démultiplié par la composition.

### 10. Les intervalles de confiance

V̂₁ et V̂_R sont des proportions de succès sur N demandes, exactement comme le taux de conformité de l'étape 7. Ils sont sans biais, ont une variance V(1 − V)/N, et on les publie avec leur intervalle de Wilson, démontré à l'étape 7 :

$$
\text{IC}_{\text{Wilson}} = \frac{\hat{V} + \dfrac{z^2}{2N} \ \pm\ z\sqrt{\dfrac{\hat{V}(1 - \hat{V})}{N} + \dfrac{z^2}{4N^2}}}{1 + \dfrac{z^2}{N}}
$$

**z = 1,96** à 95 %.

### 11. Exemple fait à la main (le code reprend ces nombres)

**Mesure.** 500 courriels de demande de crédit passent dans la boucle de l'étape 8, avec R = 2.

| Issue | Demandes | Comptage cumulé |
| --- | --- | --- |
| Valide au 1er essai | 455 | k₁ = 455 |
| Valide au 2e essai | 36 | k₂ = 491 |
| Valide au 3e essai | 6 | k₃ = 497 |
| Escaladée après 3 essais | 3 | — |

$$
\hat{V}_1 = \frac{455}{500} = 0{,}91, \qquad \hat{V}_R = \frac{497}{500} = 0{,}994, \qquad \text{escalade} = 0{,}006
$$

Intervalles de Wilson à 95 % : V₁ ∈ [0,8817 ; 0,9321] et V_R ∈ [0,9825 ; 0,9980].

**Fiabilité des relances.**

$$
\hat{p}_r^{(1)} = \frac{491 - 455}{500 - 455} = \frac{36}{45} = 0{,}8, \qquad \hat{p}_r^{(2)} = \frac{497 - 491}{500 - 491} = \frac{6}{9} \approx 0{,}667
$$

**Le modèle indépendant est trop optimiste.** Avec p = 0,91 à chaque essai, il prédit 1 − 0,09³ = 0,999271, soit 499,6 demandes valides sur 500. On en observe 497. Avec p₁ = 0,91 et p_r = 0,8 (point 6) : 1 − 0,09 × 0,2² = 0,9964, soit 498,2. C'est plus proche, mais encore au-dessus, parce que la deuxième relance réussit moins souvent que la première (0,667 contre 0,8). Les 3 dernières demandes ressemblent à une fraction irréparable (point 7) : on va lire leurs courriels au lieu d'ajouter une relance.

**Où ça casse.** Les 45 échecs du premier passage se répartissent par champ fautif :

| Champ | Erreurs | Cause typique |
| --- | --- | --- |
| `duree_mois` | 18 | « 36 » écrit en chaîne au lieu d'un entier |
| `type_pret` | 12 | « perso » hors de l'énumération |
| `emirates_id` | 9 | tirets manquants dans `784-AAAA-NNNNNNN-C` |
| `montant_aed` | 6 | « 150k » au lieu de 150000 |

Les deux premiers champs portent 30 erreurs sur 45, soit 67 %. Réécrire leur description dans le schéma (« entier, en mois, par exemple 36 », « une des valeurs : personnel, auto, immobilier ») fait monter V₁ sans toucher à R.

**Coût et escalade.** À 500 courriels par jour, 3 escalades par jour arrivent chez un analyste. Le coût moyen de la boucle reste proche du point 8 : environ 1 380 tokens d'entrée par courriel au lieu de 1 200.

---

## Effets et comportement

- **La première relance fait l'essentiel du travail.** Avec p = 0,9, elle fait passer de 0,9 à 0,99. Les suivantes rapportent dix fois moins chacune.
- **Un p faible ne se rattrape pas par R.** Il faut 10 relances pour atteindre 0,9995 avec p = 0,5, et le coût en tokens double. On améliore p.
- **Un plafond de V̂_R révèle une fraction irréparable.** Relancer n'y change rien. On corrige l'entrée ou on demande à l'utilisateur.
- **Le mode strict de l'API ne rend pas cette mesure inutile.** Il garantit la syntaxe et les types, mais pas les bornes retirées du schéma envoyé (étape 8). V₁ se mesure sur le **validateur local**, celui qui revérifie ces bornes.
- **Valide ne veut pas dire juste.** Un JSON peut passer le schéma avec une valeur fausse : un poids en livres écrit dans un champ en kilogrammes, une date du 3 décembre lue comme le 12 mars. La validation est nécessaire, pas suffisante. Les métriques de justesse viennent à l'évaluation (étape 63).

## Du symbole au code Python

| Symbole | Variable ou fonction |
| --- | --- |
| p, q, R | `p`, `1 - p`, `relances` |
| P_succ(R) | `p_succes(p, relances)` |
| 𝔼[A] | `essais_moyens(p, relances)` (formule) et `essais_moyens_somme(p, relances)` (somme des queues) |
| Gain d'une relance | `gain_relance(p, relances)` |
| R_min | `relances_min(p, cible)` |
| 1 − (1 − p₁)(1 − p_r)^R | `p_succes_deux_taux(p1, pr, relances)` |
| (1 − f)(1 − q^(R+1)) | `p_succes_irreparable(p, relances, f)` |
| 𝔼[T] | `tokens_moyens(p, relances, b, d)` |
| k₁, k₂, k₃, V̂₁, V̂_R | `comptages(issues, relances)` |
| p̂_r | `fiabilite_relances(k, N)` |
| IC de Wilson | `wilson(k, n)` |

### Déroulé, ligne par ligne

**`p_succes(p, relances)`** renvoie `1 - (1 - p) ** (relances + 1)`. La garde refuse un p hors de ]0, 1] et un nombre de relances négatif.

**`essais_moyens(p, relances)`** applique la formule fermée `(1 - (1 - p) ** (relances + 1)) / p`. **`essais_moyens_somme`** calcule la même chose par la somme `sum((1 - p) ** i for i in range(relances + 1))`, c'est-à-dire la formule des queues avant simplification. Le programme vérifie que les deux coïncident pour plusieurs valeurs : c'est la démonstration 3 vérifiée en machine.

**`gain_relance(p, relances)`** renvoie `p_succes(p, relances) - p_succes(p, relances - 1)`. Le programme vérifie qu'il vaut `p * (1 - p) ** relances`, et que le rapport entre deux gains successifs vaut `1 - p`.

**`relances_min(p, cible)`** parcourt R = 0, 1, 2… jusqu'à `p_succes(p, R) >= cible`. Le programme compare le résultat à la formule fermée avec `math.ceil` de la démonstration 5. La boucle sert de contrôle : avec un quotient qui tombe juste sur un entier, l'arrondi des flottants pourrait faire hésiter `math.ceil` d'une unité.

**`p_succes_deux_taux`** et **`p_succes_irreparable`** traduisent les points 6 et 7.

**`tokens_moyens(p, relances, b, d)`** fait `sum((1 - p) ** i * (b + i * d) for i in range(relances + 1))`, la formule du point 8.

**`simuler_boucle(...)`** est la boucle de l'étape 8 avec un faux modèle aléatoire : à chaque essai, `rng.random() < p` décide si le JSON est valide. Une fraction `f` des demandes est marquée irréparable dès le départ et n'a jamais de succès. Elle renvoie la fréquence de succès et le nombre moyen d'essais. La graine fixe rend le résultat reproductible.

**`comptages(issues, relances)`** prend la liste des issues, c'est-à-dire le numéro de l'essai qui a réussi (1, 2 ou 3) ou `None` pour une escalade, et le nombre de relances R (2 dans le programme). Pour i de 1 à R + 1, `k[i]` compte les issues dont le numéro est ≤ i. **`fiabilite_relances(k, N)`** calcule `(k[i+1] - k[i]) / (N - k[i])`.

**`main()`**, bloc par bloc.

1. Les deux résultats annoncés à l'étape 8 : 0,999 et 1,11 essai.
2. La formule des queues contre la formule fermée, sur une grille de p et de R.
3. Le tableau des gains décroissants.
4. R_min pour la cible 0,9995 : 3, 6 et 10.
5. Le coût en tokens : 1 380, puis 2 500 avec p = 0,5.
6. La composition sur 5 sorties : 0,5905 contre 0,9950.
7. La simulation, indépendante puis avec 0,6 % d'irréparables : la fréquence colle à la formule, et le plafond 1 − f apparaît.
8. Les comptages de l'exemple : V̂₁, V̂_R, Wilson, p̂_r, la prédiction trop optimiste du modèle indépendant, et la répartition des erreurs par champ.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`_garde(p, relances)`** — Cette petite fonction privée, signalée par son souligné initial, est la sentinelle postée à l'entrée des formules : elle reçoit une probabilité de succès par essai et un nombre de relances, et lève `ValueError` avec le message « il faut 0 < p <= 1 et relances >= 0 » si p sort de ]0, 1] ou si le nombre de relances est négatif. Elle ne renvoie rien quand tout va bien. `p_succes` et `essais_moyens` l'appellent en premier, si bien qu'un appel absurde échoue bruyamment au lieu de produire une probabilité négative ou une division par zéro.

**`p_succes(p, relances)`** — C'est le parieur qui calcule ses chances de gagner au moins une manche : la fonction reçoit la probabilité p qu'un essai produise un JSON valide et le nombre R de relances, fait vérifier ces entrées par `_garde`, puis renvoie 1 − (1 − p) puissance R + 1, le complément de la probabilité que les R + 1 essais échouent tous. Avec p = 0,9, elle donne 0,99 pour une relance, 0,999 pour deux, 0,9999 pour trois et 0,99999 pour quatre ; c'est aussi la brique de `gain_relance`, `relances_min` et `p_succes_irreparable`.

**`essais_moyens_somme(p, relances)`** — Celle-ci est le second témoin, qu'on interroge pour recouper la déposition du premier : elle reçoit les mêmes p et R et additionne, pour i allant de 0 à R, la probabilité (1 − p) puissance i que les i premiers essais aient échoué, c'est-à-dire la formule des queues avant toute simplification. Elle renvoie cette somme, sans passer par `_garde`. Dans `main`, elle est comparée à la formule fermée d'`essais_moyens` sur toute une grille, p valant 0,3, 0,5, 0,9, 0,99 ou 1 et R allant de 0 à 5, et les deux coïncident à chaque fois.

**`gain_relance(p, relances)`** — Cette fonction est le comptable qui mesure ce que rapporte la dernière relance ajoutée : elle reçoit p et R, et renvoie la différence entre la probabilité de succès avec R relances et celle avec R − 1. Comme `p_succes` passe par `_garde`, un appel avec R = 0 lève `ValueError`, puisqu'il demanderait le succès avec −1 relance. Avec p = 0,9, les gains successifs valent 0,09, 0,009, 0,0009 puis 0,00009 : chaque relance rapporte dix fois moins que la précédente, ce que `main` vérifie en comparant chaque gain à p(1 − p)ᴿ et le rapport de deux gains successifs à 0,1.

**`p_succes_deux_taux(p1, pr, relances)`** — Celle-ci raffine le modèle, comme un entraîneur qui sait que son joueur ne réussit pas ses rattrapages aussi bien que son premier tir : elle reçoit la probabilité de succès du premier essai, celle de chaque relance et le nombre de relances, puis renvoie 1 − (1 − p₁)(1 − pᵣ)ᴿ, la probabilité qu'au moins un essai réussisse quand les relances ont leur propre taux. Elle ne contrôle pas ses entrées. Sur les 500 courriels de la huitième section, avec p₁ = 0,91 et pᵣ = 0,8, elle prédit 498,2 succès, moins que le modèle indépendant, mais encore plus que les 497 observés.

**`p_succes_irreparable(p, relances, f)`** — Cette fonction tient compte des dossiers perdus d'avance, comme un réparateur qui sait qu'une fraction des appareils n'a plus de pièces : elle reçoit p, R et la fraction f de demandes irréparables, et renvoie (1 − f) multiplié par `p_succes(p, relances)`, si bien que le succès ne dépasse jamais le plafond 1 − f, quel que soit le nombre de relances. Elle hérite des contrôles de `_garde`. Avec p = 0,9, dix relances et f = 0,006, elle renvoie 0,994 × (1 − 0,1¹¹), et la simulation correspondante plafonne bien autour de 0,994.

**`tokens_moyens(p, relances, b, d)`** — C'est le trésorier qui chiffre la facture moyenne en tokens d'une demande : la fonction reçoit p, R, le coût b d'un premier essai et le supplément d qu'ajoute chaque relance, l'historique s'allongeant à chaque tour, puis additionne pour i de 0 à R la probabilité (1 − p) puissance i d'atteindre l'essai i + 1, multipliée par son coût b + i × d. Elle renvoie cette espérance : 1 380 tokens pour p = 0,9, b = 1 200 et d = 400, soit 15 % de plus qu'un essai unique, et 2 500 tokens quand p tombe à 0,5.

**`wilson(k, n, z)`** — Cette fonction est le statisticien prudent qui accompagne chaque taux mesuré de sa marge d'incertitude : elle reçoit le nombre k de succès, le nombre n d'essais et le quantile z, 1,96 par défaut, calcule le taux observé, le centre décalé et la demi-largeur de l'intervalle de Wilson, et renvoie les deux bornes ramenées dans [0, 1]. Contrairement à d'autres versions du parcours, elle ne contrôle pas ses entrées, et n = 0 provoquerait une division par zéro. Sur les 500 courriels, elle donne (0,8817 ; 0,9321) pour les 455 réussites du premier passage et (0,9825 ; 0,9980) pour les 497 réussites après relances.

**`comptages(issues, relances)`** — Celle-ci est le greffier qui reporte dans un registre cumulé l'issue de chaque dossier : elle reçoit la liste des issues, où chaque élément est le numéro de l'essai qui a réussi ou `None` pour une escalade, et le nombre de relances, puis renvoie un dictionnaire qui associe à chaque numéro i, de 1 à R + 1, le nombre de demandes réussies en au plus i essais. Sur 455 réussites au premier essai, 36 au deuxième, 6 au troisième et 3 escalades, elle renvoie `{1: 455, 2: 491, 3: 497}`, d'où les taux 0,910 au premier passage et 0,994 après réparation.

**`fiabilite_relances(k, n)`** — Cette fonction mesure, comme un entraîneur qui ne regarde que les rattrapages, la chance qu'une relance réussisse sachant que tout ce qui précède a échoué : elle reçoit le registre cumulé des comptages et le nombre total de demandes, et renvoie, pour chaque relance, le nombre de nouvelles réussites divisé par le nombre de demandes encore en échec avant elle. Sur l'exemple, elle donne 36 / 45 = 0,8 pour la première relance et 6 / 9 ≈ 0,667 pour la seconde : les relances réussissent moins bien que le premier essai, preuve que l'hypothèse d'indépendance est trop optimiste.

**`main()`** — C'est le professeur qui fait vérifier en machine chaque résultat du chapitre, en huit temps : il retrouve d'abord les 0,999 et 1,11 essai annoncés à l'étape 8, confronte la formule des queues à la formule fermée, imprime les gains décroissants des relances et calcule les relances minimales pour la cible 0,9995, 3, 6 et 10 selon que p vaut 0,9, 0,7 ou 0,5. Il chiffre ensuite le coût en tokens, 1 380 puis 2 500, la composition sur 5 sorties, 0,5905 contre 0,9950, et simule 20 000 demandes avec et sans irréparables, avant de dépouiller les 500 courriels : comptages, intervalles de Wilson, fiabilité des relances, prédictions trop optimistes et deux champs qui portent 67 % des échecs.

```python
"""Étape 11 — taux de validation de schéma et boucle de réparation : succès, essais, relances, coût, mesure."""
import math
import random
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _garde(p, relances):
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")


def p_succes(p, relances):
    """P_succ(R) = 1 − (1 − p)^(R+1)."""
    _garde(p, relances)
    return 1 - (1 - p) ** (relances + 1)


def essais_moyens(p, relances):
    """E[A] = (1 − (1 − p)^(R+1)) / p."""
    _garde(p, relances)
    return (1 - (1 - p) ** (relances + 1)) / p


def essais_moyens_somme(p, relances):
    """E[A] = Σ_{i=0}^{R} P(A > i) = Σ (1 − p)^i  (formule des queues)."""
    return sum((1 - p) ** i for i in range(relances + 1))


def gain_relance(p, relances):
    return p_succes(p, relances) - p_succes(p, relances - 1)


def relances_min(p, cible):
    r = 0
    while p_succes(p, r) < cible:
        r += 1
    return r


def p_succes_deux_taux(p1, pr, relances):
    return 1 - (1 - p1) * (1 - pr) ** relances


def p_succes_irreparable(p, relances, f):
    return (1 - f) * p_succes(p, relances)


def tokens_moyens(p, relances, b, d):
    return sum((1 - p) ** i * (b + i * d) for i in range(relances + 1))


def simuler_boucle(p, relances, demandes, f=0.0, graine=11):
    rng = random.Random(graine)
    succes, essais_total = 0, 0
    for _ in range(demandes):
        irreparable = rng.random() < f
        for essai in range(1, relances + 2):
            essais_total += 1
            if not irreparable and rng.random() < p:
                succes += 1
                break
    return succes / demandes, essais_total / demandes


def wilson(k, n, z=1.96):
    v = k / n
    a = z * z / n
    centre = (v + a / 2) / (1 + a)
    demi = z * math.sqrt(v * (1 - v) / n + z * z / (4 * n * n)) / (1 + a)
    return max(0.0, centre - demi), min(1.0, centre + demi)


def comptages(issues, relances):
    """issues : numéro de l'essai réussi (1..R+1) ou None si escalade. Renvoie k[1..R+1]."""
    return {i: sum(1 for x in issues if x is not None and x <= i) for i in range(1, relances + 2)}


def fiabilite_relances(k, n):
    return [(k[i + 1] - k[i]) / (n - k[i]) for i in range(1, len(k))]


def main():
    print("1. Résultats annoncés à l'étape 8 (p = 0.9, R = 2)")
    ps, ea = p_succes(0.9, 2), essais_moyens(0.9, 2)
    print(f"  P_succ = {ps:.3f}   E[essais] = {ea:.2f}")
    assert math.isclose(ps, 0.999) and math.isclose(ea, 1.11)
    assert math.isclose(ea, ps / 0.9)

    print("2. Formule des queues = formule fermée")
    for p in (0.3, 0.5, 0.9, 0.99, 1.0):
        for r in range(6):
            assert math.isclose(essais_moyens(p, r), essais_moyens_somme(p, r))
    print("  vérifié pour p dans {0.3, 0.5, 0.9, 0.99, 1} et R de 0 à 5")

    print("3. Rendements décroissants (p = 0.9)")
    for r in range(1, 5):
        g = gain_relance(0.9, r)
        print(f"  R = {r} : P_succ = {p_succes(0.9, r):.5f}   gain = {g:.5f}")
        assert math.isclose(g, 0.9 * 0.1 ** r)
        if r > 1:
            assert math.isclose(g / gain_relance(0.9, r - 1), 0.1)

    print("4. Relances minimales pour la cible 0.9995")
    for p, attendu in ((0.9, 3), (0.7, 6), (0.5, 10)):
        r = relances_min(p, 0.9995)
        formule = max(0, math.ceil(math.log(1 - 0.9995) / math.log(1 - p)) - 1)
        print(f"  p = {p} : R_min = {r}")
        assert r == attendu == formule

    print("5. Coût moyen en tokens (b = 1200, d = 400, R = 2)")
    t9, t5 = tokens_moyens(0.9, 2, 1200, 400), tokens_moyens(0.5, 2, 1200, 400)
    print(f"  p = 0.9 : {t9:.0f} tokens (+{t9 / 1200 - 1:.0%})   p = 0.5 : {t5:.0f} tokens")
    assert math.isclose(t9, 1380) and math.isclose(t5, 2500)

    print("6. Composition sur 5 sorties structurées")
    sans, avec = p_succes(0.9, 0) ** 5, p_succes(0.9, 2) ** 5
    print(f"  sans réparation : {sans:.4f}   avec R = 2 : {avec:.4f}")
    assert math.isclose(sans, 0.59049) and math.isclose(avec, 0.999 ** 5)

    print("7. Simulation de la boucle (20 000 demandes)")
    freq, essais = simuler_boucle(0.9, 2, 20_000)
    print(f"  indépendant : succès = {freq:.4f} (théorie 0.9990)   essais = {essais:.3f} (théorie 1.110)")
    assert abs(freq - 0.999) < 0.002 and abs(essais - 1.11) < 0.02
    freq_f, _ = simuler_boucle(0.9, 10, 20_000, f=0.006)
    print(f"  6 ‰ irréparables, R = 10 : succès = {freq_f:.4f} (plafond 1 − f = 0.9940)")
    assert freq_f <= 1 - 0.006 + 0.002
    assert math.isclose(p_succes_irreparable(0.9, 10, 0.006), 0.994 * (1 - 0.1 ** 11))

    print("8. Mesure sur 500 courriels")
    issues = [1] * 455 + [2] * 36 + [3] * 6 + [None] * 3
    k = comptages(issues, 2)
    n = len(issues)
    v1, vr = k[1] / n, k[3] / n
    l1, h1 = wilson(k[1], n)
    lr, hr = wilson(k[3], n)
    print(f"  k = {k}   V1 = {v1:.3f} [{l1:.4f} ; {h1:.4f}]   VR = {vr:.3f} [{lr:.4f} ; {hr:.4f}]")
    assert k == {1: 455, 2: 491, 3: 497} and v1 <= vr
    assert (round(l1, 4), round(h1, 4)) == (0.8817, 0.9321)
    assert (round(lr, 4), round(hr, 4)) == (0.9825, 0.9980)
    pr = fiabilite_relances(k, n)
    print(f"  fiabilité des relances : {pr[0]:.3f} puis {pr[1]:.3f}")
    assert math.isclose(pr[0], 0.8) and math.isclose(pr[1], 2 / 3)
    indep = p_succes(0.91, 2) * n
    deux = p_succes_deux_taux(0.91, 0.8, 2) * n
    print(f"  prédit : indépendant {indep:.1f}, deux taux {deux:.1f}, observé {k[3]}")
    assert indep > deux > k[3]
    erreurs = Counter({"duree_mois": 18, "type_pret": 12, "emirates_id": 9, "montant_aed": 6})
    assert sum(erreurs.values()) == n - k[1]
    top2 = sum(v for _, v in erreurs.most_common(2)) / (n - k[1])
    print(f"  deux champs portent {top2:.0%} des échecs du premier passage : {[c for c, _ in erreurs.most_common(2)]}")
    assert math.isclose(top2, 30 / 45)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Résultats annoncés à l'étape 8 (p = 0.9, R = 2)
  P_succ = 0.999   E[essais] = 1.11
2. Formule des queues = formule fermée
  vérifié pour p dans {0.3, 0.5, 0.9, 0.99, 1} et R de 0 à 5
3. Rendements décroissants (p = 0.9)
  R = 1 : P_succ = 0.99000   gain = 0.09000
  R = 2 : P_succ = 0.99900   gain = 0.00900
  R = 3 : P_succ = 0.99990   gain = 0.00090
  R = 4 : P_succ = 0.99999   gain = 0.00009
4. Relances minimales pour la cible 0.9995
  p = 0.9 : R_min = 3
  p = 0.7 : R_min = 6
  p = 0.5 : R_min = 10
5. Coût moyen en tokens (b = 1200, d = 400, R = 2)
  p = 0.9 : 1380 tokens (+15%)   p = 0.5 : 2500 tokens
6. Composition sur 5 sorties structurées
  sans réparation : 0.5905   avec R = 2 : 0.9950
7. Simulation de la boucle (20 000 demandes)
  indépendant : succès = 0.9990 (théorie 0.9990)   essais = 1.112 (théorie 1.110)
  6 ‰ irréparables, R = 10 : succès = 0.9938 (plafond 1 − f = 0.9940)
8. Mesure sur 500 courriels
  k = {1: 455, 2: 491, 3: 497}   V1 = 0.910 [0.8817 ; 0.9321]   VR = 0.994 [0.9825 ; 0.9980]
  fiabilité des relances : 0.800 puis 0.667
  prédit : indépendant 499.6, deux taux 498.2, observé 497
  deux champs portent 67% des échecs du premier passage : ['duree_mois', 'type_pret']
OK — toutes les vérifications sont passées.
```

La simulation de la ligne 7 utilise une graine fixe (`graine=11`). Avec une autre graine, les fréquences bougent à la quatrième décimale et restent dans les tolérances des `assert`.

Ce que le programme montre : la boucle de réparation n'est pas un « réessaie jusqu'à ce que ça marche ». Elle a un taux de succès calculable, un coût calculable et un plafond mesurable. Et les comptages réels disent quand le modèle mathématique simple cesse d'être vrai.

---

## Squelette algorithmique

Ce fichier contient deux algorithmes : la boucle de réparation qui produit les mesures, et le calcul qui choisit le nombre de relances R à partir d'une fiabilité visée. Le second est celui qu'on lance quand on configure un agent.

```text
ALGORITHME MesurerLaBoucle
ENTRÉES : issues de N demandes (numéro de l'essai réussi, ou « escalade »), R
SORTIE  : V̂₁, V̂_R, fiabilités des relances

  POUR i DE 1 À R + 1 FAIRE
      kᵢ ← nombre de demandes réussies au plus tard à l'essai i
  FIN POUR
  V̂₁ ← k₁ / N           V̂_R ← k_R+1 / N
  POUR i DE 1 À R FAIRE
      p̂_r(i) ← (k_i+1 − kᵢ) / (N − kᵢ)
  FIN POUR
  RETOURNER V̂₁, V̂_R, p̂_r, et les intervalles de Wilson de V̂₁ et V̂_R

ALGORITHME ChoisirR
ENTRÉES : fiabilité d'un essai p, cible c
SORTIE  : le plus petit R tel que 1 − (1 − p)^(R+1) ≥ c

  R ← 0
  TANT QUE 1 − (1 − p)^(R+1) < c FAIRE
      R ← R + 1
  FIN TANT QUE
  RETOURNER R                     (égal à ⌈ln(1 − c) / ln(1 − p)⌉ − 1)
```

**Complexité.** Mesurer la boucle coûte O(N × R) avec la double boucle ci-dessus, ou O(N + R) si l'on compte d'abord combien de demandes ont réussi à chaque essai puis qu'on cumule. Choisir R coûte O(R_min) tours de boucle, soit au plus une dizaine dans les cas réalistes, contre O(1) pour la formule fermée, mais la boucle évite les erreurs d'arrondi de `ceil`. La simulation de vérification coûte O(demandes × (R + 1)) tirages aléatoires.

**Du squelette au code.** `MesurerLaBoucle` correspond à `comptages`, `fiabilite_relances` et `wilson`. `ChoisirR` correspond à `relances_min`, que le programme compare à la formule fermée avec `math.ceil`. Les autres fonctions (`p_succes`, `essais_moyens`, `gain_relance`, `tokens_moyens`) calculent les formules du chapitre, et `simuler_boucle` rejoue la boucle avec un faux modèle aléatoire pour vérifier qu'elles prédisent bien les fréquences observées.

## Cas d'usage réels aux Émirats

Les taux, volumes, seuils et coûts ci-dessous sont illustratifs. Les règles citées (CBUAE, VARA, WPS, formats de l'Emirates ID et de l'IBAN, codes ICD-10) sont à confirmer avec le texte en vigueur avant toute mise en production.

### Banque — des demandes de crédit extraites de courriels

Une banque de détail de Dubaï transforme chaque jour environ 500 courriels de demande de prêt personnel en objets `DemandeCredit` (étape 8). Le tableau de bord affiche chaque matin V̂₁ et V̂_R avec leurs intervalles de Wilson, sur la veille et sur les trente derniers jours. Après une mise à jour du modèle, V̂₁ passe de 0,91 à 0,84, et l'intervalle de la journée ne recoupe plus celui de la période de référence. La baisse est réelle, pas un hasard. Le décompte par champ montre que `duree_mois` arrive désormais en chaîne (« 36 mois ») dans un cas sur dix. L'équipe ajoute un exemple au champ du schéma et, en attendant, une normalisation en code qui transforme « 36 mois » en 36 avant la validation. V̂_R n'avait presque pas bougé (0,994 → 0,990), grâce aux relances, mais le coût moyen en tokens avait augmenté d'environ 11 % (point 8 : 1 360 tokens par courriel à p = 0,91, 1 507 à p = 0,84). Le taux d'escalade sert au planning : 0,6 % de 500, cela fait 3 dossiers par jour pour l'analyste de permanence. Le plafond d'endettement de la CBUAE reste vérifié après le schéma, par une règle qui compare plusieurs champs.

### Immobilier — des annonces dictées en une phrase

Une agence de Dubaï et d'Abu Dhabi laisse ses agents dicter leurs annonces (« 2BR Marina 1250 sqft 2.4M ready »), qu'un agent IA transforme en fiche structurée. Au lancement, V̂₁ vaut 0,86 et la boucle tourne avec R = 2. Le décompte par champ montre que la moitié des échecs viennent de `prix_aed`, que le modèle recopie « 2.4M » au lieu de 2400000. Deux options sont sur la table. Augmenter R coûte des tokens à chaque annonce fautive : avec p = 0,86, une relance de plus ne rapporte que 0,86 × 0,14³ ≈ 0,0024 (point 4). Réécrire la description du champ (« nombre entier en AED, sans abréviation : 2400000 ») ne coûte rien à l'usage. C'est la seconde option qui est retenue : V̂₁ monte à 0,95 et le coût moyen par annonce baisse. Le prix au sqft se calcule ensuite sans ambiguïté sur la fiche validée.

### Crypto — un ordre de swap borné, où l'on ne relance pas l'ambiguïté

Une plateforme d'actifs virtuels agréée par la VARA prépare des ordres de swap pour des clients institutionnels. Le champ `slippage_max` est borné à [0 ; 0,05]. Quand un client écrit « slippage 0,5 », le modèle produit 0,5, que le validateur refuse. La relance donne parfois 0,005 (0,5 %), parfois 0,05, parfois encore 0,5 : le modèle ne peut pas savoir ce que le client voulait dire. C'est une fraction irréparable au sens du point 7, et relancer revient à laisser le modèle deviner. La plateforme fixe donc R = 0 pour ce champ précis : toute erreur sur `slippage_max` renvoie une question au client. Le taux de validation sert ici à mesurer un coût (combien de questions on pose), pas la sécurité. La sécurité est garantie par le validateur lui-même : une liste d'erreurs vide équivaut à une instance valide (étape 8, démonstration 1), donc aucun ordre hors bornes ne part, quel que soit V̂₁.

### Assurance — une date de sinistre que la relance ne sait pas trancher

Un assureur auto et santé fait remplir les déclarations d'accrochage par un agent conversationnel. Le champ `date_sinistre` impose le format `AAAA-MM-JJ`. Les comptages d'un mois montrent p̂_r^(1) = 0,75 mais p̂_r^(2) = 0,20 : la seconde relance ne sert presque plus à rien. En lisant les cas, l'équipe trouve que les échecs persistants viennent d'assurés qui écrivent « 12/03 » sans année ni ordre clair. La réponse est la même que pour la crypto. On passe à R = 1, puis, en cas de second échec, l'agent demande à l'assuré « le 12 mars ou le 3 décembre ? ». Les déclarations ressaisies à la main par les gestionnaires baissent. La boucle ne prend plus 3 essais pour finir de toute façon chez un humain.

### RH — un fichier de salaires WPS où chaque ligne compte

Un cabinet de paie prépare pour ses clients les fichiers de salaires transmis par le WPS. L'agent extrait des fiches de paie une ligne structurée par salarié : identifiant, IBAN, salaire fixe, variable, jours. Un fichier n'est accepté que si **toutes** ses lignes sont valides. Pour une PME de 40 salariés, la composition du point 9 change tout. Sans réparation (p = 0,9), le fichier passe entièrement dans 0,9⁴⁰ ≈ 1,5 % des cas. Avec R = 2 (0,999 par ligne), il passe dans 0,999⁴⁰ ≈ 96,1 % des cas. Le cabinet ajoute un dernier niveau : les lignes encore invalides sont isolées et montrées à un gestionnaire, au lieu de bloquer le fichier entier. On suit le nombre de fichiers rejetés par la banque et le délai moyen entre la réception des fiches et l'envoi du fichier.

### BTP — le budget en tokens du contrôle des factures

Un groupe de construction fait extraire environ 3 000 factures par mois dans le format `ControleFacture`, avec R = 2. Chaque premier appel envoie environ 1 200 tokens (prompt système, schéma, texte de la facture). Chaque relance ajoute environ 400 tokens : la réponse fautive et la liste des erreurs. Avec V₁ = 0,9, le point 8 donne 1 380 tokens par facture en moyenne, soit environ 540 000 tokens de plus par mois que sans relance. C'est le chiffre qui entre dans le budget de l'équipe (étape 72). Quand un nouveau fournisseur envoie des factures scannées de mauvaise qualité, V₁ tombe à 0,5 pour ses factures et leur coût double (2 500 tokens). L'équipe demande alors au fournisseur des PDF natifs plutôt que d'augmenter R.

### Secteur public — des chiffres arabes que le motif refuse

Un service public en ligne accessible par UAE Pass extrait l'Emirates ID des demandes écrites en arabe et en anglais. Le schéma impose le motif `^784-[0-9]{4}-[0-9]{7}-[0-9]$`. V̂₁ vaut 0,97 en anglais et 0,81 en arabe, avec des intervalles de Wilson disjoints : l'écart est réel. Les échecs en arabe viennent des chiffres arabes-indiens (٧٨٤ au lieu de 784). Le modèle les recopie fidèlement, la classe `[0-9]` les refuse, et la relance échoue presque toujours (p̂_r ≈ 0,3), parce que le modèle « corrige » souvent autre chose. La solution n'est ni le prompt ni R : une fonction de normalisation convertit les chiffres arabes-indiens en chiffres occidentaux **avant** la validation. V̂₁ en arabe remonte au niveau de l'anglais. Leçon générale : quand une erreur est mécanique et prévisible, on la corrige en code, pas avec le modèle.

### Santé — des codes diagnostics dans les demandes de remboursement

Un prestataire de santé de Dubaï prépare les demandes de remboursement envoyées aux assureurs. L'agent extrait des comptes rendus les codes ICD-10, avec un motif du type `^[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?$`. La cible interne est qu'au moins 99,95 % des demandes partent avec des codes au bon format. Avec un premier essai à p = 0,7, la démonstration 5 donne R_min = 6 relances : coût inacceptable et délai trop long. L'équipe améliore d'abord p, avec une liste des codes les plus fréquents dans le prompt et une normalisation des espaces et des points en code, jusqu'à p = 0,9. Avec ce p, R_min = 3. Le format n'est que la première barrière : un code valide peut être le mauvais code. La justesse du codage est vérifiée par un codeur médical sur un échantillon, avec son propre taux et son propre intervalle.

### Logistique — un JSON valide avec un poids faux

Un transitaire de la zone franche de Jebel Ali fait extraire les bordereaux d'expédition de ses clients : poids brut en kg, nombre de colis, port de destination. V̂_R vaut 0,998, et pourtant les douanes renvoient des déclarations. L'audit montre que des bordereaux américains donnent le poids en livres, et que le modèle recopie le nombre dans `poids_kg`. Le JSON est valide, le schéma est respecté, et la valeur est fausse d'un facteur 2,2. Le taux de validation ne pouvait pas le voir. L'équipe ajoute au schéma un champ obligatoire `unite_poids_source` dans une énumération `["kg", "lb"]` et fait la conversion en code. Elle ajoute aussi une règle inter-champs qui compare le poids aux colis déclarés. Leçon : un taux de validation élevé mesure la forme, jamais le fond.

---

## Pièges et limites

- **Confondre essais et relances.** R relances, c'est R + 1 essais. La formule utilise l'exposant R + 1.
- **Croire que la formule indépendante prédit la production.** Les cas difficiles restent difficiles. On mesure p̂_r à chaque relance et on compare (point 6).
- **Relancer une ambiguïté.** Si l'information manque ou est ambiguë, le modèle devine. On demande à l'utilisateur (crypto, assurance).
- **Monter R au lieu de monter p.** Les gains décroissent comme q^R, le coût en tokens croît à chaque relance.
- **Mesurer V₁ sur le mode strict de l'API.** La grammaire garantit la syntaxe ; les bornes retirées du schéma envoyé ne sont vérifiées que par le validateur local.
- **Publier V̂_R sans V̂₁.** Un V̂_R de 0,99 peut cacher un V̂₁ de 0,6 et un coût en tokens doublé.
- **Prendre « valide » pour « juste ».** Le schéma contraint la forme. Une unité, une date ou un code faux passent.

### Exercice feuille blanche

1. Sans regarder le code, redémontrer 𝔼[A] = (1 − q^(R+1)) / p par la formule des queues, puis vérifier à la main que p = 0,8 et R = 3 donnent 1,248 essai.
2. Prédire, puis vérifier : avec p = 0,6, combien de relances faut-il pour atteindre 0,999 ? (Réponse : ln(0,001) / ln(0,4) = 7,54, donc R + 1 = 8 et R = 7.)
3. Avec N = 300, k₁ = 240, k₂ = 282, k₃ = 288, calculer V̂₁, V̂_R, p̂_r^(1) et p̂_r^(2). Le modèle indépendant est-il plausible ? (Réponses : 0,80 ; 0,96 ; 0,70 ; 0,333 ; non, la seconde relance réussit deux fois moins souvent que la première.)
4. Trouver le bug : `return 1 - (1 - p) ** relances`. Que renvoie la fonction pour R = 0, et quelle conclusion fausse en tirerait-on ? (Réponse : 0, comme si un appel sans relance ne réussissait jamais.)

## Pour aller plus loin

- La fiabilité composée et ses bornes sans indépendance sont démontrées à l'[étape 1](<../01-Agent/01-Agent-Definitions-Fondamentaux.md>).
- L'intervalle de Wilson est démontré à l'[étape 7](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>).
- Une relance est un cas particulier de « réessayer une action ». Les relances d'un outil qui a des effets de bord demandent en plus l'idempotence : [étape 12](<12-Outils-Definitions-Fondamentaux.md>).
- Réussir **au moins une fois** sur k essais (pass@k) et réussir **à chaque fois** (pass^k) sont deux mesures différentes, traitées à l'évaluation.

> Suite : [Outils : définitions fondamentales](<12-Outils-Definitions-Fondamentaux.md>) — étape 12.
