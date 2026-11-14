# Étape 72 — Complexité Quadratique et Optimisation des Coûts (Token Management)

> Étape 72 du parcours · Prérequis : [Erlang C et file M/M/c](<71-Erlang-C.md>) · Suite : [Batching continu et PagedAttention](<72b-Batching-Continu-et-PagedAttention.md>)

**Dossier :** 12-Production-Couts-Optimisation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team, Forward-Deployed Engineers  
**Nom du fichier :** 72-Couts-et-Gestion-des-Tokens.md

## Définition

Un fournisseur de modèle facture chaque appel au nombre de tokens : ceux que l'agent envoie en entrée (prompt système, contexte, historique, résultats d'outils) et ceux que le modèle génère en sortie, chacun à son propre prix. Ce prix est **linéaire** : deux fois plus de tokens d'entrée coûtent deux fois plus. Ce qui est quadratique, c'est autre chose. D'une part, le calcul des scores d'attention à l'intérieur du modèle croît comme le carré de la longueur du contexte n (étape 31). D'autre part, un agent qui renvoie tout l'historique à chaque étape paie, sur une session de K étapes, une somme de tailles qui croît comme K². La gestion des tokens (token management) regroupe les techniques qui cassent cette croissance : fenêtre glissante, résumé, recherche des seuls passages utiles, et cache du préfixe, qui ne retire aucun token mais en baisse le prix.

## Rôle dans un agent

Un ingénieur AI Agentic doit concevoir des agents rentables. Dans la boucle percevoir → décider → agir → observer, chaque tour renvoie au modèle le prompt système, les outils, l'historique et les nouvelles observations : c'est le « percevoir » qui coûte, et il coûte de plus en plus à mesure que la boucle tourne. Le calcul de ce fichier sert au composant de **mémoire** de travail, qui décide ce que l'on garde (fenêtre, résumé, étape 13 ter), au **retriever**, qui limite les documents injectés (étape 18), et au **garde-fou de budget**, qui arrête une boucle avant qu'elle ne coûte plus que sa valeur. Si l'agent envoie tout l'historique à chaque fois, la facture d'API explose ; il faut décider mathématiquement de ce qui est envoyé au modèle.

## Équation complète

La fonction de coût d'un appel, puis d'une session de K étapes :

$$
\text{Coût} = N_{in} \times P_{in} + N_{out} \times P_{out}
$$

$$
C_{total} = P_{in} \sum_{k=1}^{K} N_{in}^{(k)} + P_{out} \sum_{k=1}^{K} N_{out}^{(k)}
$$

Sans élagage, l'étape k relit tout l'historique, et le total d'entrée est quadratique en K :

$$
N_{in}^{(k)} = S_0 + (k-1)\,\Delta
$$

$$
\sum_{k=1}^{K} N_{in}^{(k)} = K S_0 + \Delta\,\frac{K(K-1)}{2} = \frac{\Delta}{2} K^2 + \left(S_0 - \frac{\Delta}{2}\right) K
$$

Avec une fenêtre glissante qui garde les M derniers échanges, le total devient linéaire en K (forme fermée valable pour K ≥ M + 1) :

$$
N_{in,\,fen}^{(k)} = S_0 + \min(k-1,\, M)\,\Delta
$$

$$
\sum_{k=1}^{K} N_{in,\,fen}^{(k)} = K S_0 + \Delta\, \frac{M\,(2K - M - 1)}{2} \;\le\; K\,(S_0 + M \Delta)
$$

Avec en plus un cache du préfixe S₀ (écriture au facteur w au premier appel, lecture au facteur f ensuite) :

$$
C_{in,\,fen+cache} = P_{in} \left( S_0\,\bigl(w + f\,(K-1)\bigr) + \Delta\, \frac{M\,(2K - M - 1)}{2} \right)
$$

Sans fenêtre, mais en relisant dans le cache tout ce qui a déjà été envoyé :

$$
C_{in,\,hist+cache} = P_{in} \left( w S_0 + (K-1)\,(w \Delta + f S_0) + f \Delta\, \frac{(K-1)(K-2)}{2} \right)
$$

La complexité du calcul d'attention pour un contexte de n tokens de dimension d :

$$
O(n^2 \cdot d)
$$

## Décryptage des symboles

$$
N_{in}
$$

Nombre de tokens envoyés en entrée lors d'un appel : prompt système, contexte, historique, résultats d'outils · entier ≥ 0 · variable Python : `tokens_in`.

$$
N_{out}
$$

Nombre de tokens générés par le modèle lors d'un appel · entier ≥ 0 · variable Python : `tokens_out`.

$$
P_{in}
$$

Prix d'un token d'entrée, en USD par token : 3 USD par million dans ce fichier, soit 0,000003 USD par token (prix illustratif) · variable Python : `prix_in`.

$$
P_{out}
$$

Prix d'un token de sortie : 15 USD par million ici, cinq fois le prix d'entrée (prix illustratif ; le rapport varie selon les fournisseurs et les modèles) · variable Python : `prix_out`.

$$
K
$$

Nombre d'étapes (allers-retours avec le modèle) d'une session de l'agent · entier ≥ 1 · variable Python : `K`.

$$
k
$$

Numéro de l'étape courante, de 1 à K · variable Python : `k`.

$$
S_0
$$

Taille fixe du prompt envoyé à chaque étape (prompt système, définitions d'outils, contexte de départ), en tokens · variable Python : `s0`.

$$
\Delta
$$

Nombre de tokens qu'ajoute chaque étape à l'historique (réponse du modèle et résultat d'outil), supposé constant · variable Python : `delta`.

$$
M
$$

Taille de la fenêtre glissante, en nombre d'échanges conservés · entier ≥ 0 · variable Python : `M`.

$$
f
$$

Facteur de prix d'un token **lu** dans le cache, en fraction du prix d'entrée : 0,10 ici · variable Python : `facteur_lecture`.

$$
w
$$

Facteur de prix d'un token **écrit** dans le cache, en multiple du prix d'entrée : 1,25 ici · variable Python : `facteur_ecriture`.

$$
n
$$

Longueur du contexte vu par le modèle lors d'un appel, en tokens · variable Python : `n`.

$$
d
$$

Dimension des vecteurs sur lesquels l'attention calcule ses produits scalaires · variable Python : `d`.

$$
C_{total}
$$

Coût total d'une session, en USD · variable Python : `par_session`, `session_opt`.

Les facteurs f = 0,10 et w = 1,25 sont ceux d'une grille courante pour un cache de courte durée (environ 5 minutes, renouvelée à chaque lecture) ; certains modèles lisent le cache encore moins cher, et un cache d'une heure s'écrit plus cher. Ils restent illustratifs : on les vérifie sur la grille du fournisseur avant tout chiffrage.

## Démonstration

### 1. Pourquoi le total d'entrée est quadratique

On suppose que la partie fixe du prompt vaut S₀ et que chaque étape ajoute Δ tokens à l'historique. À l'étape k, l'agent renvoie le prompt fixe et les k − 1 échanges précédents : N⁽ᵏ⁾ = S₀ + (k − 1)Δ. On somme sur les K étapes, en séparant les deux termes, parce qu'une somme de sommes se coupe en deux :

$$
\sum_{k=1}^{K} \bigl(S_0 + (k-1)\Delta\bigr) = \sum_{k=1}^{K} S_0 + \Delta \sum_{j=0}^{K-1} j
$$

Le premier terme vaut K S₀. Pour le second, on écrit la somme 0 + 1 + … + (K − 1) une fois à l'endroit et une fois à l'envers, puis on additionne terme à terme : chaque paire vaut K − 1, et il y a K paires, donc deux fois la somme vaut K(K − 1) (l'argument de Gauss) :

$$
\sum_{j=0}^{K-1} j = \frac{K(K-1)}{2}
$$

On remplace et on développe :

$$
N_{in,\,total} = K S_0 + \Delta \frac{K(K-1)}{2} = \frac{\Delta}{2} K^2 + \left(S_0 - \frac{\Delta}{2}\right) K
$$

Le terme dominant est (Δ/2)K² : le total d'entrée, donc le coût d'entrée P_in × N_in,total, est en O(K²). Avec K = 15, S₀ = 2 000 et Δ = 500 : 15 × 2 000 + 500 × 15 × 14/2 = 30 000 + 52 500 = 82 500 tokens, alors que la session ne contient « que » 9 000 tokens à la dernière étape.

### 2. Doubler K ne quadruple pas encore la facture

Notons a = Δ/2 et b = S₀ − Δ/2. Le rapport entre 2K et K étapes vaut

$$
\frac{a (2K)^2 + b (2K)}{a K^2 + b K} = \frac{4 a K + 2 b}{a K + b} \;\xrightarrow[K \to \infty]{}\; 4
$$

parce qu'en divisant le numérateur et le dénominateur par K, les termes en b/K tendent vers 0. À K = 15 : a = 250 et b = 1 750, et le rapport vaut (4 × 250 × 15 + 3 500)/(250 × 15 + 1 750) = 18 500/5 500 ≈ 3,36. L'ancienne version de ce fichier disait « proche de 4 » : 3,36 n'est pas proche de 4, parce qu'à K = 15 le terme linéaire bK (26 250 tokens) pèse encore presque la moitié du terme quadratique aK² (56 250). Le rapport vaut 3,62 à K = 30, 3,95 à K = 300. Le fichier de fondements (étape 43) affirmait de même que doubler les étapes « quadruple » le coût : c'est la limite, pas la valeur à K = 15.

### 3. La fenêtre glissante rend le total linéaire

Avec une fenêtre de M échanges, l'étape k renvoie min(k − 1, M) échanges. Pour K ≥ M + 1, les M + 1 premières étapes ont des fenêtres de 0, 1, …, M échanges, et les K − M − 1 suivantes une fenêtre pleine :

$$
\sum_{k=1}^{K} \min(k-1, M) = \sum_{j=0}^{M} j + (K - M - 1)\, M = \frac{M(M+1)}{2} + M (K - M - 1) = \frac{M (2K - M - 1)}{2}
$$

La dernière égalité s'obtient en mettant M en facteur : (M + 1)/2 + K − M − 1 = (2K − M − 1)/2. Le total vaut donc K S₀ + Δ M (2K − M − 1)/2 : il est **linéaire** en K, de pente S₀ + MΔ. Il est aussi inférieur à la borne K(S₀ + MΔ), qui supposerait la fenêtre pleine dès l'étape 1 : l'écart vaut exactement Δ M (M + 1)/2. Avec K = 15 et M = 4 : 30 000 + 500 × 4 × 25/2 = 55 000 tokens, contre une borne de 60 000 ; l'écart vaut 500 × 4 × 5/2 = 5 000. Le fichier de fondements (étape 43) donnait 60 000 comme « tokens d'entrée totaux » : c'est la borne, la somme exacte vaut 55 000.

### 4. Le cache ne retire aucun token, il en change le prix

Un cache de préfixe garde côté fournisseur le début du prompt déjà traité. Quand la requête suivante commence par exactement les mêmes tokens, ceux-ci sont relus au facteur f au lieu d'être facturés plein tarif. Les tokens restent **envoyés** et comptés : N_in ne baisse pas, c'est son prix moyen qui baisse. L'ancienne version de ce fichier disait l'inverse (« N_in envoyé au modèle reste bas ») et appelait cette technique « CAG - Context Augmentation » ; CAG veut dire Cache-Augmented Generation, une approche qui place une base de connaissances stable dans le contexte mis en cache au lieu de la chercher à chaque question.

**Fenêtre et cache du seul S₀.** Au premier appel, S₀ est écrit (facteur w) ; aux K − 1 suivants, il est relu (facteur f). Les échanges de la fenêtre changent à chaque pas, ils restent au tarif plein. En factorisant P_in :

$$
C_{in} = P_{in}\left(w S_0 + f S_0 (K-1) + \Delta \frac{M (2K - M - 1)}{2}\right)
$$

Avec w = 1,25 et f = 0,10 : 2 000 × (1,25 + 1,4) + 25 000 = 30 300 « tokens équivalents », soit 0,0909 USD. L'ancienne version du code comptait l'écriture au tarif plein (w = 1) et trouvait 0,0894 USD.

**Historique complet, entièrement relu dans le cache.** À l'étape k ≥ 2, tout ce qui a été envoyé à l'étape k − 1, soit S₀ + (k − 2)Δ tokens, est relu au facteur f, et seuls les Δ nouveaux tokens sont écrits au facteur w. En sommant sur k = 2 à K et en réutilisant l'argument de Gauss du point 1 pour la somme des (k − 2) :

$$
C_{in} = P_{in}\left(w S_0 + \sum_{k=2}^{K} \bigl(f (S_0 + (k-2)\Delta) + w \Delta\bigr)\right)
= P_{in}\left(w S_0 + (K-1)(w\Delta + f S_0) + f \Delta \frac{(K-1)(K-2)}{2}\right)
$$

Le terme en K² est toujours là, mais son coefficient vaut fΔ/2 au lieu de Δ/2 : la croissance reste quadratique, dix fois plus lente. À K = 15, on trouve 2 500 + 14 × 825 + 4 550 = 18 600 tokens équivalents, soit 0,0558 USD : c'est moins cher que la fenêtre avec cache. Mais à partir de K = 55 dans cet exemple, la fenêtre redevient moins chère, parce que son coût est linéaire. Et la fenêtre a d'autres avantages que le cache n'apporte pas : le contexte reste court, donc le temps de réponse et le calcul d'attention aussi, et l'on ne bute jamais sur la longueur maximale du contexte.

### 5. Le « ×4 » ne vaut que pour l'attention

Pour un contexte de n tokens, le calcul des scores d'attention forme une matrice n × n de produits scalaires de dimension d, soit n² d multiplications (étape 31). Doubler n multiplie ce calcul par (2n)²/n² = 4. Mais le prix d'API est linéaire en n : doubler le contexte double la facture d'entrée, il ne la quadruple pas. Les autres couches du modèle (projections, réseau feed-forward) coûtent en n d², linéaire en n. L'ancienne définition de ce fichier disait que doubler le contexte « coûte 4 fois plus cher en calcul » : c'est vrai pour la seule matrice d'attention, pas pour la facture ni pour l'ensemble du calcul. Avec n = 4 000 et d = 128, n² d = 2,048 milliards d'opérations ; à n = 8 000, 8,192 milliards.

### 6. Le RAG ne divise pas le coût par le rapport des documents

Envoyer 3 documents au lieu de 50 divise par 50/3 ≈ 16,7 la partie « documents » du prompt, pas le prompt entier : le prompt système et la question ne changent pas, et les tokens de sortie non plus. L'ancienne version de ce fichier disait « divise Nᵢₙ par 15 et le coût par 15 » ; 50/3 vaut 16,7, et le facteur réel sur le coût est plus petit. Avec un prompt système de 1 500 tokens, une question de 100 tokens et des documents de 400 tokens, on passe de 21 600 à 2 800 tokens d'entrée : 7,7 fois moins, pas 16,7.

### 7. Exemple fait à la main (le code reprend ces nombres)

K = 15, S₀ = 2 000, Δ = 500, M = 4, P_in = 3 USD par million, P_out = 15 USD par million, 100 000 sessions par mois.

- Naïf : 82 500 tokens d'entrée, 0,2475 USD ; 15 × 500 = 7 500 tokens de sortie, 0,1125 USD ; 0,36 USD par session, 432 000 USD par an (dont 297 000 pour la seule entrée).
- Fenêtre seule : 55 000 tokens d'entrée.
- Fenêtre et cache de S₀ : 0,0909 USD d'entrée, 0,2034 USD par session avec la sortie, 244 080 USD par an, soit 43,5 % de moins que le naïf.
- Historique entier en cache : 0,0558 USD d'entrée, toujours 82 500 tokens envoyés.

Le fichier de fondements (étape 43) annonçait 0,0612 USD par session, 73 440 USD par an et −75,2 % : ces chiffres ignorent les tokens de sortie, qui ne se mettent pas en cache et pèsent ici 0,1125 USD par session à eux seuls.

## Effets et comportement

- **Si le nombre d'étapes K double**, le total d'entrée sans élagage est multiplié par un facteur qui tend vers 4 (3,36 à K = 15) ; avec une fenêtre, il est seulement doublé (un peu plus que doublé, à cause du démarrage de la fenêtre).
- **Si le contexte Nᵢₙ d'un appel double**, son coût d'entrée double, mais le calcul de la matrice d'attention quadruple, et le temps avant le premier token s'allonge.
- **Si l'on met en cache le préfixe stable**, Nᵢₙ ne change pas : les tokens sont toujours envoyés, mais le prix effectif de la partie relue tombe au facteur f. Le cache a une durée de vie : une requête qui arrive après son expiration repaie l'écriture.
- **Si l'on demande à l'agent de réfléchir longtemps** (par exemple Tree of Thoughts, ou un long raisonnement visible), Nₒᵤₜ explose. Comme Pₒᵤₜ > Pᵢₙ (5 fois ici), le coût grimpe vite, et ni la fenêtre ni le cache ne réduisent les tokens de sortie.
- **Si l'on remplace 50 documents par les 3 meilleurs**, la partie « documents » est divisée par 16,7, mais le coût total bien moins : 7,7 fois moins sur l'entrée dans l'exemple, et moins encore si l'on compte la sortie.

## Du symbole au code Python

Sans élagage, l'étape k réenvoie tout l'historique. Le déroulé additionne ces tailles une par une, puis montre ce que la fenêtre et le cache retirent de la somme. Copiez dans `cout_tokens.py`.

| Symbole | Variable ou fonction |
|---|---|
| N_in de l'étape k, naïf | `tokens_entree_naif(k, s0, delta)` |
| Σ N_in, boucle et forme fermée | `total_naif(K, s0, delta)`, `formule_quadratique(K, s0, delta)` |
| Σ N_in avec fenêtre | `total_fenetre(K, s0, delta, M)`, `formule_fenetre(K, s0, delta, M)` |
| Coût = N_in P_in + N_out P_out | `cout(tokens_in, tokens_out, prix_in, prix_out)` |
| fenêtre + cache de S₀ | `cout_avec_cache(...)`, `formule_cache_fenetre(...)` |
| historique entier en cache | `cout_cache_historique(...)`, `formule_cache_historique(...)` |
| f, w | `facteur_lecture`, `facteur_ecriture` |
| n² d | `ops_attention(n, d)` |

### Déroulé, ligne par ligne

Les constantes, lues une fois dans `main` : `K = 15` étapes, `s0 = 2_000` tokens de prompt fixe, `delta = 500` tokens ajoutés à chaque étape, `prix_in = 3.00 / 1_000_000` USD par token d'entrée, `prix_out = 15.00 / 1_000_000` en sortie, et `sessions_par_an = 100_000 * 12`. Tous les prix sont illustratifs. Les nombres s'affichent avec le séparateur `_` de Python (`82_500`), pour qu'aucune virgule ne se lise comme une virgule décimale.

**`tokens_entree_naif(k, s0, delta)`** renvoie `s0 + (k - 1) * delta`.

- Étape 1 : 2 000 + 0 = 2 000. Rien n'a encore été dit.
- Étape 2 : 2 000 + 500 = 2 500. On renvoie le premier échange en plus du prompt.
- Étape 15 : 2 000 + 14 × 500 = 9 000. Les 14 échanges précédents sont relus, alors qu'ils ont déjà été payés aux étapes d'avant.

**`total_naif`** fait `sum(... for k in range(1, K + 1))`. `range` s'arrête avant `K + 1`, donc `k` vaut 1, 2, …, 15. La somme des quinze tailles vaut 82 500.

**`formule_quadratique`** écrit la même somme sans boucle : `(delta / 2) * K * K + (s0 - delta / 2) * K`.

- Premier terme : (500/2) × 15² = 250 × 225 = 56 250. C'est le morceau en K², celui qui vient de 0 + 1 + ⋯ + 14 = 15 × 14/2.
- Deuxième terme : (2 000 − 250) × 15 = 26 250.
- Total 82 500, le même que la boucle. Les deux fonctions doivent rester égales : le `main` le vérifie pour K = 15, puis pour K = 1, 2, 7 et 40. Si l'une change, l'`assert` s'arrête.

**Le rapport 2K/K.** Doubler `K` à 30 : la formule donne 277 500, et 277 500/82 500 = 3,36. Pas 2, pas encore 4. La boucle du bloc 2 affiche aussi 3,622 pour K = 30 → 60, 3,954 pour 300 → 600 et 3,995 pour 3 000 → 6 000 : le rapport monte vers 4 à mesure que le terme en K² écrase le terme en K (démonstration, point 2).

**`cout(tokens_in, tokens_out, prix_in, prix_out)`** renvoie `tokens_in * prix_in + tokens_out * prix_out`.

- Entrée : 82 500 × 3 × 10⁻⁶ = 0,2475 USD.
- Sortie : on pose `tokens_out = K * delta`, soit 7 500, parce que chaque étape écrit 500 tokens neufs. 7 500 × 15 × 10⁻⁶ = 0,1125 USD.
- Session : 0,3600 USD. Année : ce nombre fois 1,2 million de sessions, soit 432 000 USD, et 1 586 520 AED au taux fixe de 3,6725 AED par USD. Le cours citait 297 000 USD en ne comptant que l'entrée ; ici la sortie est ajoutée, parce que la fonction de coût a les deux termes.

**`total_fenetre(K, s0, delta, M)`** avec `M = 4`.

- La taille de l'étape `k` devient `s0 + min(k - 1, M) * delta`. `min` empêche l'historique de dépasser 4 échanges.
- Étape 1 : 2 000. Étape 5 : 2 000 + 4 × 500 = 4 000. Étapes 6 à 15 : toujours 4 000, au lieu de monter jusqu'à 9 000.
- Somme exacte : 55 000. **`formule_fenetre`** donne le même nombre sans boucle, `K * s0 + delta * M * (2 * K - M - 1) / 2`, soit 30 000 + 500 × 4 × 25/2 ; pour K < M + 1, la fenêtre n'est jamais pleine et la fonction renvoie la formule naïve. Le plafond `K * (s0 + M * delta) = 15 * 4000 = 60 000` suppose que la fenêtre est pleine dès l'étape 1 ; l'`assert` vérifie que l'écart vaut exactement ΔM(M + 1)/2 = 5 000.

**`cout_avec_cache`**, fenêtre plus cache du seul préfixe.

- Boucle sur `k`. `prix_prefixe` vaut `prix_in * facteur_ecriture` à `k == 1` (le préfixe de 2 000 tokens est écrit dans le cache, à 1,25 fois le tarif), puis `prix_in * facteur_lecture` ensuite (relu au dixième du tarif).
- `dynamique = min(k - 1, M) * delta` reste au plein tarif : ces tokens changent à chaque étape quand la fenêtre glisse, ils ne forment pas un préfixe stable.
- Sur les 15 étapes, l'entrée vaut 0,0909 USD, la même valeur que **`formule_cache_fenetre`**. Avec la sortie, qui ne se met pas en cache, la session vaut 0,2034 USD et l'année 244 080 USD, 43,5 % de moins que le naïf. L'ancienne version comptait l'écriture au tarif plein et trouvait 0,0894 USD d'entrée.

**`cout_cache_historique`**, l'historique entier relu dans le cache.

- Étape 1 : `s0 * facteur_ecriture * prix_in`, l'écriture du préfixe.
- Étape k ≥ 2 : `deja_envoye = tokens_entree_naif(k - 1, s0, delta)` tokens sont relus au facteur 0,10, et les `delta` nouveaux sont écrits au facteur 1,25. À l'étape 15, cela fait 8 500 tokens relus et 500 écrits.
- Résultat : 0,0558 USD à K = 15, la valeur de **`formule_cache_historique`**, alors que 82 500 tokens sont toujours envoyés. À K = 60, il vaut 0,4102 USD contre 0,3879 USD pour la fenêtre avec cache : l'`assert` vérifie que la croissance quadratique a fini par rattraper la solution linéaire.

**Le bloc RAG.** `avant = 1_500 + 100 + 50 * 400 = 21_600` et `apres = 1_500 + 100 + 3 * 400 = 2_800` : le rapport vaut 7,7, alors que 50/3 vaut 16,7.

**`ops_attention(n, d)`** renvoie `n * n * d`.

- À 4 000 tokens et `d = 128` : 4 000² × 128 = 2,048 milliards d'opérations.
- À 8 000 tokens : quatre fois plus, parce que `n` est au carré. Le prix d'API de l'entrée, lui, n'aurait fait que doubler. Les deux coûts ne bougent pas ensemble.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tokens_entree_naif(k, s0, delta)`** — Cette fonction est le facteur qui pèse le colis envoyé au modèle à l'étape k, quand l'agent n'oublie rien et renvoie chaque fois toute la correspondance passée : elle reçoit le numéro d'étape, la taille du prompt fixe S₀ et le nombre de tokens Δ ajoutés par étape, et renvoie S₀ + (k − 1)Δ. Avec S₀ = 2 000 et Δ = 500, le colis pèse 2 000 tokens à l'étape 1, 2 500 à l'étape 2 et déjà 9 000 à l'étape 15, où les quatorze échanges précédents sont relus alors qu'ils ont déjà été payés.

**`total_naif(K, s0, delta)`** — Celle-ci est le comptable qui additionne, ligne après ligne, tous les bordereaux d'une session : elle reçoit le nombre d'étapes K, S₀ et Δ, appelle `tokens_entree_naif` pour chaque étape de 1 à K et renvoie la somme des tailles, c'est-à-dire tous les tokens d'entrée facturés pendant la session. Pour les 15 étapes du cas support client, elle trouve 82 500 tokens, et `main` s'en sert comme référence que la forme fermée doit retrouver exactement.

**`formule_quadratique(K, s0, delta)`** — Cette fonction écrit la même somme sans boucle, comme un mathématicien qui remplace la colonne de chiffres par une seule équation : elle reçoit K, S₀ et Δ, et renvoie (Δ/2)K² + (S₀ − Δ/2)K, une parabole en K qui montre d'où vient la facture qui s'emballe. Pour K = 15, les deux termes valent 56 250 et 26 250, soit 82 500 comme la boucle ; `main` vérifie l'égalité pour K = 1, 2, 7, 15 et 40, puis s'en sert pour montrer que doubler K multiplie l'entrée par 3,36, et non par 2.

**`total_fenetre(K, s0, delta, M)`** — Celle-ci refait l'addition avec un agent qui ne garde en mémoire que les M derniers échanges, comme un secrétaire qui ne joint au courrier que les quatre dernières lettres : elle reçoit K, S₀, Δ et la largeur de fenêtre M, et additionne pour chaque étape S₀ + min(k − 1, M)Δ, le `min` empêchant l'historique de dépasser M échanges. Elle renvoie le total des tokens d'entrée ; avec M = 4, chaque étape plafonne à 4 000 tokens à partir de l'étape 5, et la session ne coûte plus que 55 000 tokens au lieu de 82 500.

**`formule_fenetre(K, s0, delta, M)`** — Cette fonction donne la forme fermée de la somme précédente : elle reçoit K, S₀, Δ et M, renvoie la formule naïve de `formule_quadratique` si K < M + 1, parce que la fenêtre n'est alors jamais pleine, et sinon K·S₀ + Δ·M·(2K − M − 1)/2. Pour K = 15 et M = 4, cela fait 30 000 + 25 000 = 55 000, le même nombre que la boucle, et `main` vérifie cette égalité pour K = 5, 6, 15 et 100, puis que le plafond de 60 000 tokens dépasse la vraie somme de exactement 5 000.

**`cout(tokens_in, tokens_out, prix_in, prix_out)`** — Celle-ci est la caisse enregistreuse qui transforme des tokens en dollars : elle reçoit le nombre de tokens d'entrée, celui de sortie et leurs prix unitaires, exprimés en USD par token, et renvoie N_in × P_in + N_out × P_out, sans rien vérifier. Pour la session naïve, 82 500 tokens à 3 USD le million donnent 0,2475 USD et 7 500 tokens de sortie à 15 USD le million 0,1125 USD, soit 0,36 USD, ce qui fait 432 000 USD, ou 1 586 520 AED, pour 1,2 million de sessions par an.

**`cout_avec_cache(K, s0, delta, M, prix_in, facteur_lecture, facteur_ecriture)`** — Cette fonction chiffre une session qui combine la fenêtre glissante et un cache du seul prompt fixe, comme un imprimeur qui grave une fois la plaque de l'en-tête et ne paie ensuite que le tirage : elle reçoit K, S₀, Δ, M, le prix d'entrée et deux facteurs, 0,10 pour relire le cache et 1,25 pour l'écrire, puis facture à chaque étape le préfixe S₀ au tarif d'écriture à l'étape 1 et au tarif de lecture ensuite, plus les tokens de la fenêtre au plein tarif, car ils changent à chaque pas. Elle renvoie le coût d'entrée en USD, 0,0909 USD pour K = 15, et la session tombe alors à 0,2034 USD avec la sortie, soit 244 080 USD par an.

**`formule_cache_fenetre(K, s0, delta, M, prix_in, f, w)`** — Celle-ci est le contrôleur qui refait le calcul du cache avec fenêtre d'un seul trait de plume : elle reçoit les mêmes grandeurs, avec f = 0,10 et w = 1,25 par défaut, et renvoie P_in × (S₀(w + f(K − 1)) + ΔM(2K − M − 1)/2), une écriture qui suppose la fenêtre pleine, c'est-à-dire K ≥ M + 1, sans le vérifier elle-même. Pour K = 15, le préfixe compte pour 2 000 × 2,65 = 5 300 tokens équivalents et la fenêtre pour 25 000, soit 0,0909 USD au tarif de 3 USD le million, exactement ce que trouve la boucle de `cout_avec_cache`.

**`cout_cache_historique(K, s0, delta, prix_in, facteur_lecture, facteur_ecriture)`** — Cette fonction chiffre une autre stratégie, celle d'un agent qui garde tout son historique mais le fait relire dans le cache, comme un lecteur qui retrouve ses notes déjà surlignées : elle reçoit K, S₀, Δ, le prix d'entrée et les deux facteurs, compte l'écriture du préfixe à l'étape 1, puis, à chaque étape suivante, relit au facteur 0,10 tout le prompt de l'étape précédente et écrit au facteur 1,25 les Δ nouveaux tokens. Elle renvoie le coût d'entrée en USD : 0,0558 USD pour K = 15, bien qu'on envoie toujours 82 500 tokens, mais 0,4102 USD pour K = 60, au-dessus des 0,3879 USD de la fenêtre avec cache, car la relecture reste quadratique.

**`formule_cache_historique(K, s0, delta, prix_in, f, w)`** — Celle-ci est la forme fermée de la stratégie précédente : elle reçoit K, S₀, Δ, le prix d'entrée et les facteurs f = 0,10 et w = 1,25, et renvoie P_in × (wS₀ + (K − 1)(wΔ + fS₀) + fΔ(K − 1)(K − 2)/2), où le dernier terme, en K², rappelle que même relu à prix réduit, l'historique entier finit par coûter cher. Pour K = 15, les trois morceaux valent 2 500, 11 550 et 4 550 tokens équivalents, soit 18 600 × 3 × 10⁻⁶ = 0,0558 USD, le nombre que `main` exige de la boucle de `cout_cache_historique`.

**`ops_attention(n, d)`** — Cette fonction mesure un coût que la facture d'API ne montre pas, celui du calcul d'attention, où chaque token doit regarder chacun des autres comme les convives d'un banquet qui se saluent tous deux à deux : elle reçoit la longueur du contexte n et la dimension d, et renvoie n × n × d. À 4 000 tokens et d = 128, cela fait 2 048 000 000 opérations, et à 8 000 tokens quatre fois plus, alors que le prix d'entrée n'aurait fait que doubler, ce que vérifie la dernière section de `main`.

**`main()`** — C'est le contrôleur de gestion qui déroule le dossier du support client en sept chapitres, avec K = 15, S₀ = 2 000, Δ = 500 et des prix illustratifs de 3 et 15 USD le million : il montre d'abord la somme de 82 500 tokens et son égalité avec la parabole, puis le rapport 3,36 quand on double K, et la facture naïve de 432 000 USD par an. Il passe ensuite à la fenêtre de quatre échanges et au cache du préfixe, qui ramènent l'année à 244 080 USD, compare au cache de tout l'historique à K = 15 puis à K = 60, chiffre le RAG qui passe de 21 600 à 2 800 tokens, et termine sur l'attention qui quadruple quand le contexte double ; chaque nombre est verrouillé par un `assert`.

```python
"""Étape 72 — coût d'API, croissance K², fenêtre glissante, cache de préfixe (prix illustratifs)."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

AED_PAR_USD = 3.6725


def tokens_entree_naif(k: int, s0: int, delta: int) -> int:
    """N_in^(k) = S0 + (k − 1) Δ. L'étape k relit tout l'historique."""
    return s0 + (k - 1) * delta


def total_naif(K: int, s0: int, delta: int) -> int:
    """Σ_{k=1}^{K} N_in^(k), additionné étape par étape."""
    return sum(tokens_entree_naif(k, s0, delta) for k in range(1, K + 1))


def formule_quadratique(K: int, s0: int, delta: int) -> float:
    """La même somme, fermée : (Δ/2) K² + (S0 − Δ/2) K."""
    return (delta / 2) * K * K + (s0 - delta / 2) * K


def total_fenetre(K: int, s0: int, delta: int, M: int) -> int:
    """N_in^(k) = S0 + min(k−1, M) Δ, additionné étape par étape."""
    return sum(s0 + min(k - 1, M) * delta for k in range(1, K + 1))


def formule_fenetre(K: int, s0: int, delta: int, M: int) -> float:
    """Forme fermée pour K ≥ M + 1 : K·S0 + Δ·M·(2K − M − 1)/2."""
    if K < M + 1:
        return formule_quadratique(K, s0, delta)   # la fenêtre n'est jamais pleine
    return K * s0 + delta * M * (2 * K - M - 1) / 2


def cout(tokens_in: float, tokens_out: float, prix_in: float, prix_out: float) -> float:
    """Coût = N_in × P_in + N_out × P_out. Les prix sont en USD par token."""
    return tokens_in * prix_in + tokens_out * prix_out


def cout_avec_cache(K: int, s0: int, delta: int, M: int, prix_in: float,
                    facteur_lecture: float = 0.10, facteur_ecriture: float = 1.25) -> float:
    """Fenêtre glissante + cache du seul préfixe S0.

    Étape 1 : S0 est écrit dans le cache (tarif d'écriture). Étapes suivantes : S0 est relu (tarif de lecture).
    Les échanges de la fenêtre changent à chaque pas : ils restent au tarif plein. Rien n'est retiré du prompt.
    """
    total = 0.0
    for k in range(1, K + 1):
        prix_prefixe = prix_in * (facteur_ecriture if k == 1 else facteur_lecture)
        dynamique = min(k - 1, M) * delta
        total += s0 * prix_prefixe + dynamique * prix_in
    return total


def formule_cache_fenetre(K: int, s0: int, delta: int, M: int, prix_in: float,
                          f: float = 0.10, w: float = 1.25) -> float:
    """P_in · (S0 (w + f (K − 1)) + Δ M (2K − M − 1)/2), pour K ≥ M + 1."""
    return prix_in * (s0 * (w + f * (K - 1)) + delta * M * (2 * K - M - 1) / 2)


def cout_cache_historique(K: int, s0: int, delta: int, prix_in: float,
                          facteur_lecture: float = 0.10, facteur_ecriture: float = 1.25) -> float:
    """Historique complet, sans fenêtre, mais tout le préfixe déjà envoyé est relu dans le cache.

    Étape 1 : S0 écrit. Étape k ≥ 2 : le prompt de l'étape k − 1 est relu, les Δ nouveaux tokens sont écrits.
    """
    total = s0 * facteur_ecriture * prix_in
    for k in range(2, K + 1):
        deja_envoye = tokens_entree_naif(k - 1, s0, delta)
        total += (deja_envoye * facteur_lecture + delta * facteur_ecriture) * prix_in
    return total


def formule_cache_historique(K: int, s0: int, delta: int, prix_in: float,
                             f: float = 0.10, w: float = 1.25) -> float:
    """P_in · (w S0 + (K − 1)(w Δ + f S0) + f Δ (K − 1)(K − 2)/2)."""
    return prix_in * (w * s0 + (K - 1) * (w * delta + f * s0) + f * delta * (K - 1) * (K - 2) / 2)


def ops_attention(n: int, d: int) -> int:
    """O(n² · d) : chaque paire de tokens, et un produit de dimension d."""
    return n * n * d


def main() -> None:
    # Chiffres du cas support client (prix illustratifs, en USD par million de tokens).
    K = 15
    s0 = 2_000
    delta = 500
    prix_in = 3.00 / 1_000_000
    prix_out = 15.00 / 1_000_000
    sessions_par_an = 100_000 * 12

    print("=== 1. La somme qui devient un carré ===")
    print("  tokens d'entrée envoyés à chaque étape, sans mémoire :")
    for k in (1, 2, 3, 15):
        print(f"    étape {k:2d} : {tokens_entree_naif(k, s0, delta):_} tokens")
    brut = total_naif(K, s0, delta)
    ferme = formule_quadratique(K, s0, delta)
    print(f"  total sur {K} étapes = {brut:_.0f}")
    print(f"  formule (Δ/2)K² + (S0 − Δ/2)K = {ferme:_.0f}")
    assert brut == 82_500 and abs(brut - ferme) < 1e-6
    for K_test in (1, 2, 7, 40):
        assert abs(total_naif(K_test, s0, delta) - formule_quadratique(K_test, s0, delta)) < 1e-6

    print("\n=== 2. Doubler les étapes ne double pas la facture d'entrée ===")
    for etapes in (15, 30, 300, 3000):
        rapport = formule_quadratique(2 * etapes, s0, delta) / formule_quadratique(etapes, s0, delta)
        print(f"  K = {etapes:4d} → 2K   rapport des tokens d'entrée cumulés = {rapport:.3f}")
    r15 = formule_quadratique(30, s0, delta) / formule_quadratique(15, s0, delta)
    assert abs(r15 - 277_500 / 82_500) < 1e-12 and round(r15, 2) == 3.36
    print("  le rapport tend vers 4 quand K grandit ; à K = 15, le terme en K pèse encore")

    print("\n=== 3. Facture annuelle, architecture naïve ===")
    tokens_out = K * delta
    par_session = cout(brut, tokens_out, prix_in, prix_out)
    annuelle = par_session * sessions_par_an
    print(f"  entrée {brut:_.0f} × 3 USD/M = {brut * prix_in:.4f} USD")
    print(f"  sortie {tokens_out:_.0f} × 15 USD/M = {tokens_out * prix_out:.4f} USD")
    print(f"  session = {par_session:.4f} USD ; 1.2 M sessions par an = {annuelle:_.0f} USD = {annuelle * AED_PAR_USD:_.0f} AED")
    assert abs(brut * prix_in - 0.2475) < 1e-9 and abs(tokens_out * prix_out - 0.1125) < 1e-9
    assert abs(annuelle - 432_000) < 1e-6 and abs(brut * prix_in * sessions_par_an - 297_000) < 1e-6

    print("\n=== 4. Fenêtre M = 4, puis cache du prompt système ===")
    M = 4
    fenetre = total_fenetre(K, s0, delta, M)
    borne = K * (s0 + M * delta)
    print(f"  somme exacte avec fenêtre = {fenetre:_.0f}   formule fermée = {formule_fenetre(K, s0, delta, M):_.0f}")
    print(f"  le cours écrit 15 × 4 000 = {borne:_.0f} : c'est le plafond, pas la somme (écart ΔM(M+1)/2 = {borne - fenetre:_})")
    assert fenetre == 55_000 and fenetre <= borne and borne - fenetre == delta * M * (M + 1) // 2
    for K_test in (5, 6, 15, 100):
        assert abs(total_fenetre(K_test, s0, delta, M) - formule_fenetre(K_test, s0, delta, M)) < 1e-6
    entree_cache = cout_avec_cache(K, s0, delta, M, prix_in)
    assert abs(entree_cache - formule_cache_fenetre(K, s0, delta, M, prix_in)) < 1e-12
    session_opt = entree_cache + tokens_out * prix_out          # la sortie ne se met pas en cache
    annuelle_opt = session_opt * sessions_par_an
    print(f"  entrée fenêtre + cache de S0 (écriture ×1.25, lecture ×0.10) = {entree_cache:.4f} USD")
    print(f"  session entrée + sortie = {session_opt:.4f} USD ; année = {annuelle_opt:_.0f} USD")
    print(f"  écart avec le naïf = {annuelle - annuelle_opt:_.0f} USD par an ({(annuelle_opt - annuelle) / annuelle:+.1%})")
    assert abs(entree_cache - 0.0909) < 1e-9 and abs(annuelle_opt - 244_080) < 1e-6

    print("\n=== 5. Sans fenêtre, mais tout l'historique relu dans le cache ===")
    hist = cout_cache_historique(K, s0, delta, prix_in)
    assert abs(hist - formule_cache_historique(K, s0, delta, prix_in)) < 1e-12
    print(f"  entrée = {hist:.4f} USD   (tokens envoyés : toujours {brut:_})")
    for etapes in (15, 60):
        print(f"  K = {etapes:2d}   naïf = {formule_quadratique(etapes, s0, delta) * prix_in:.4f} USD"
              f"   cache d'historique = {cout_cache_historique(etapes, s0, delta, prix_in):.4f} USD"
              f"   fenêtre + cache = {cout_avec_cache(etapes, s0, delta, M, prix_in):.4f} USD")
    assert abs(hist - 0.0558) < 1e-9
    assert cout_cache_historique(60, s0, delta, prix_in) > cout_avec_cache(60, s0, delta, M, prix_in)

    print("\n=== 6. RAG : 3 documents au lieu de 50 ===")
    systeme, question, par_doc = 1_500, 100, 400
    avant, apres = systeme + question + 50 * par_doc, systeme + question + 3 * par_doc
    print(f"  documents : 50/3 = {50 / 3:.1f} fois moins ; prompt entier : {avant:_} → {apres:_} tokens, {avant / apres:.1f} fois moins")
    assert round(50 / 3, 1) == 16.7 and round(avant / apres, 1) == 7.7

    print("\n=== 7. Le contexte que l'attention va relire ===")
    for n in (4_000, 8_000):
        print(f"  n = {n:_}   opérations d'attention ∝ {ops_attention(n, d=128):_.0f}")
    print(f"  rapport (8000/4000)² = {ops_attention(8000, 128) / ops_attention(4000, 128):.0f}")
    print("  Le coût API d'entrée double. Le calcul des scores d'attention quadruple.")
    assert ops_attention(8000, 128) == 4 * ops_attention(4000, 128) and ops_attention(4000, 128) == 2_048_000_000
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
=== 1. La somme qui devient un carré ===
…
    étape 15 : 9_000 tokens
  total sur 15 étapes = 82_500
  formule (Δ/2)K² + (S0 − Δ/2)K = 82_500
=== 2. Doubler les étapes ne double pas la facture d'entrée ===
  K =   15 → 2K   rapport des tokens d'entrée cumulés = 3.364
  K = 3000 → 2K   rapport des tokens d'entrée cumulés = 3.995
=== 3. Facture annuelle, architecture naïve ===
  session = 0.3600 USD ; 1.2 M sessions par an = 432_000 USD = 1_586_520 AED
=== 4. Fenêtre M = 4, puis cache du prompt système ===
  somme exacte avec fenêtre = 55_000   formule fermée = 55_000
  entrée fenêtre + cache de S0 (écriture ×1.25, lecture ×0.10) = 0.0909 USD
  session entrée + sortie = 0.2034 USD ; année = 244_080 USD
=== 5. Sans fenêtre, mais tout l'historique relu dans le cache ===
  K = 15   naïf = 0.2475 USD   cache d'historique = 0.0558 USD   fenêtre + cache = 0.0909 USD
  K = 60   naïf = 3.0150 USD   cache d'historique = 0.4102 USD   fenêtre + cache = 0.3879 USD
=== 6. RAG : 3 documents au lieu de 50 ===
  documents : 50/3 = 16.7 fois moins ; prompt entier : 21_600 → 2_800 tokens, 7.7 fois moins
…
OK — toutes les vérifications sont passées.
```

Le chiffre utile n'est pas le prix d'un token. C'est la somme, sur les K allers-retours, de tout ce qui est renvoyé. Une fenêtre et un cache de préfixe n'agissent pas sur Pₒᵤₜ : les tokens que l'agent écrit se paient au tarif de sortie à chaque étape, et c'est souvent le poste qui reste après qu'on a assaini l'entrée.

## Squelette algorithmique

Toutes les fonctions du fichier suivent le même schéma : elles reçoivent la forme d'une session (nombre d'étapes K, prompt fixe S₀, ajout par étape Δ, éventuellement la fenêtre M et les facteurs du cache) et les prix, et rendent un nombre de tokens ou un coût en USD. L'idée est de calculer, étape par étape, combien de tokens partent et à quel tarif chacun est facturé, puis de vérifier que la somme obtenue par la boucle coïncide avec la forme fermée démontrée plus haut.

```text
ALGORITHME CoûtEntréeSession
ENTRÉES : K ≥ 1, S0, Δ, prix d'entrée P, stratégie ∈ {naïf, fenêtre, fenêtre+cache, historique+cache},
          taille de fenêtre M, facteur de lecture f, facteur d'écriture w
SORTIE : coût d'entrée de la session, en USD
  total ← 0
  POUR k DE 1 À K FAIRE
    SI stratégie = naïf ALORS
      total ← total + (S0 + (k − 1) × Δ) × P
    SINON SI stratégie = fenêtre ALORS
      total ← total + (S0 + min(k − 1, M) × Δ) × P
    SINON SI stratégie = fenêtre+cache ALORS
      SI k = 1 ALORS facteur ← w SINON facteur ← f FIN SI
      total ← total + S0 × facteur × P + min(k − 1, M) × Δ × P
    SINON                                         // historique entier relu dans le cache
      SI k = 1 ALORS
        total ← total + w × S0 × P
      SINON
        total ← total + (f × (S0 + (k − 2) × Δ) + w × Δ) × P
      FIN SI
    FIN SI
  FIN POUR
  RETOURNER total

ALGORITHME CoûtSession
ENTRÉES : coût d'entrée E, tokens de sortie par étape Δ, K, prix de sortie Pout
SORTIE : coût total de la session
  RETOURNER E + K × Δ × Pout                      // la sortie ne se met jamais en cache

ALGORITHME PlusPetitKoùFenêtreGagne
ENTRÉES : S0, Δ, M, P, f, w
SORTIE : le premier K où fenêtre+cache coûte moins que historique+cache
  K ← M + 1
  TANT QUE CoûtEntréeSession(K, historique+cache) ≤ CoûtEntréeSession(K, fenêtre+cache) FAIRE
    K ← K + 1
  FIN TANT QUE
  RETOURNER K                                     // 55 avec les nombres du fichier
```

**Complexité :** chaque branche de `CoûtEntréeSession` fait un nombre constant d'opérations par étape, donc O(K) en temps et O(1) en mémoire, puisqu'on ne garde qu'un total. Les formes fermées (`formule_quadratique`, `formule_fenetre`, `formule_cache_fenetre`, `formule_cache_historique`) font quelques multiplications : O(1). `CoûtSession` est O(1). `PlusPetitKoùFenêtreGagne` appelle deux fois une fonction en O(K) pour chaque K essayé, soit O(K*²) pour une réponse K* ; avec les formes fermées à la place des boucles, elle tombe à O(K*), et l'on pourrait même résoudre l'inégalité du second degré directement. Le coût que le fichier mesure n'est pas celui de ces algorithmes, qui est négligeable, mais celui de l'agent qu'ils décrivent : sans fenêtre, il envoie O(K²) tokens sur une session, et le modèle calcule à chaque appel une attention en O(n² d) sur un contexte de n tokens.

**Du squelette au code :** la branche « naïf » est `tokens_entree_naif` appelée dans la boucle de `total_naif`, et sa forme fermée est `formule_quadratique`. La branche « fenêtre » est `total_fenetre` (forme fermée `formule_fenetre`). La branche « fenêtre+cache » est `cout_avec_cache` : le `SI k = 1` est l'expression `facteur_ecriture if k == 1 else facteur_lecture`, et sa forme fermée est `formule_cache_fenetre`. La branche « historique+cache » est `cout_cache_historique`, qui commence par l'écriture de S₀ puis boucle de `k = 2` à `K` (forme fermée `formule_cache_historique`). `CoûtSession` est l'appel à `cout(...)` au bloc 3 et la ligne `session_opt = entree_cache + tokens_out * prix_out` au bloc 4. `PlusPetitKoùFenêtreGagne` n'a pas de fonction dans le bloc : le bloc 5 de `main()` en vérifie le résultat aux deux bornes, K = 15 (le cache d'historique gagne) et K = 60 (la fenêtre gagne) ; l'écrire en Python est l'exercice 3.

## Cas d'usage réels aux Émirats

Tous les prix sont illustratifs (3 USD par million de tokens d'entrée, 15 USD par million en sortie, cache lu au dixième et écrit à 1,25 fois) ; on refait le calcul avec la grille réelle du fournisseur et le modèle choisi. La conversion en AED utilise le taux fixe de 3,6725 AED par USD.

### Banque — le service client et ses 1,2 million de sessions par an

Une banque de détail de Dubaï fait traiter les demandes de ses clients (carte bloquée, contestation d'opération, échéancier de prêt) par un agent qui résout un incident en 15 étapes en moyenne, avec un prompt fixe de 2 000 tokens et 500 tokens ajoutés à chaque étape. À 100 000 sessions par mois, l'architecture naïve coûte 432 000 USD par an, soit 1 586 520 AED, dont 297 000 USD pour la seule entrée. Une fenêtre de 4 échanges avec cache du prompt système ramène la facture à 244 080 USD (896 384 AED), et relire tout l'historique dans le cache la ramènerait à 201 960 USD (741 698 AED) pour ces sessions courtes. L'équipe choisit pourtant la fenêtre : les sessions de contestation dépassent parfois 55 étapes, où la fenêtre redevient la moins chère, et renvoyer moins d'historique limite aussi la quantité de données financières personnelles transmises à chaque appel. Les faits qui ne doivent jamais sortir de la fenêtre (numéro de dossier, montant contesté) sont recopiés dans le prompt fixe, qui est mis en cache. Les réponses sur un crédit continuent de passer par l'outil de ratio d'endettement de la CBUAE, quelle que soit la stratégie de mémoire. Les indicateurs suivis sont le coût par session résolue et la part de sessions qui dépassent 55 étapes.

### Immobilier — trois annonces au lieu de cinquante

Un promoteur de Dubaï et d'Abu Dhabi a d'abord fait répondre son agent en lui donnant, à chaque question, les 50 fiches de projets disponibles (400 tokens chacune), soit 21 600 tokens d'entrée avec le prompt système et la question. En ne gardant que les 3 fiches les plus proches (recherche hybride, étapes 23 et 24), l'entrée tombe à 2 800 tokens : 7,7 fois moins, et non les 16,7 fois que promettait le rapport 50/3. En comptant 400 tokens de réponse, une question passe de 0,0708 à 0,0144 USD, un facteur 4,9 seulement, parce que la sortie ne change pas. Sur 30 000 questions par mois, cela fait 2 124 USD (environ 7 800 AED) contre 432 USD (environ 1 587 AED). Le risque de la coupe est de perdre la bonne fiche : l'équipe mesure le rappel à 3 (étape 25) avant de couper, et cite toujours le prix en AED/sqft et les frais de transfert DLD de 4 % depuis un outil, jamais depuis une fiche du contexte. Les indicateurs suivis sont le coût par question et le rappel à 3 sur un jeu de questions de référence.

### Assurance — un raisonnement trop long, que le cache ne sauve pas

Un assureur auto et santé fait instruire les déclarations de sinistre par un agent qui, dans sa première version, développait un raisonnement visible de 3 000 tokens pour chaque dossier, même simple. Au prix de sortie illustratif de 15 USD par million, cela fait 0,045 USD de sortie par dossier, contre 0,0075 USD pour une réponse de 500 tokens. Sur 20 000 dossiers par mois, l'écart vaut 750 USD par mois, et aucune fenêtre ni aucun cache n'y change rien, parce qu'ils n'agissent que sur l'entrée. La décision est de réserver le raisonnement long aux dossiers que le score de risque (étape 67) envoie en revue, et de demander une réponse courte et structurée pour les autres, avec une longueur de sortie bornée. Il ne s'agit pas de raccourcir la justification due à l'assuré : la décision finale reste documentée par le gestionnaire, sous la supervision de la CBUAE. L'indicateur suivi est le nombre moyen de tokens de sortie par dossier, par catégorie de sinistre.

### RH — un dossier d'embauche de 60 étapes

Un cabinet RH présent dans plusieurs émirats confie à un agent tout le parcours d'un recrutement : offre, permis d'entrée, visite médicale, Emirates ID, contrat MOHRE, ouverture du compte salaire pour le WPS. Un dossier compte 60 étapes. Sans élagage, l'entrée coûte 3,015 USD par dossier, contre 0,3879 USD avec une fenêtre de 4 échanges et un cache du prompt fixe, auxquels s'ajoutent 0,45 USD de sortie dans les deux cas. Sur 2 000 dossiers par mois, l'entrée passe de 6 030 USD à 776 USD. La fenêtre a un risque propre : un fait donné à l'étape 3 (la date d'arrivée prévue, le type de visa) disparaît du contexte à l'étape 8. L'agent écrit donc chaque fait administratif dans une mémoire structurée (étape 15 bis), relue à chaque étape dans le prompt fixe, plutôt que de compter sur l'historique. Les données d'identité restent des données personnelles au sens de la PDPL, et la fenêtre réduit le nombre de fois où elles transitent. Les indicateurs suivis sont le coût par dossier et le nombre d'erreurs causées par un fait sorti de la fenêtre.

### BTP — un contrat de 60 000 tokens relu vingt fois

Un groupe de construction de Dubaï fait interroger par un agent un contrat de sous-traitance de 60 000 tokens (retenues de garantie, pénalités de retard, TVA à 5 % sur les situations de travaux). Sans cache, chaque question paie 60 000 × 3 USD par million = 0,18 USD d'entrée, et vingt questions coûtent 3,60 USD. Avec un cache du contrat, la première question l'écrit (0,225 USD) et les dix-neuf suivantes le relisent à 0,018 USD : 0,567 USD au total. Mais le cache a une durée de vie de quelques minutes, renouvelée à chaque lecture : si l'ingénieur pose ses questions à vingt minutes d'intervalle, chaque question repaie l'écriture et le total monte à 4,50 USD, plus cher que sans cache. La décision est de regrouper les questions sur un même contrat dans une session courte, ou de choisir une durée de cache plus longue, plus chère à l'écriture, quand le rythme de travail l'exige. Le calcul d'attention sur 60 000 tokens reste lourd, et l'on découpe le contrat par clauses (étape 18) dès que les questions portent sur une seule section. L'indicateur suivi est la part des tokens d'entrée effectivement lus dans le cache.

### Secteur public — une démarche de 30 étapes en arabe et en anglais

Une entité de services publics en ligne, accessible par UAE Pass, accompagne les usagers dans une démarche qui demande une trentaine d'échanges (pièces justificatives, paiement des frais, prise de rendez-vous), en arabe ou en anglais. Sans élagage, une session envoie 277 500 tokens d'entrée ; avec une fenêtre de 4 échanges, 115 000, soit 2,4 fois moins. Le nombre de tokens d'un même texte dépend du tokenizer et de la langue : l'équipe mesure Δ séparément pour les sessions en arabe et en anglais, au lieu de supposer la même valeur, parce que le terme en K² est proportionnel à Δ. La PDPL demande de ne traiter que les données nécessaires : la fenêtre sert aussi cette exigence, puisque les pièces d'identité citées au début de la démarche ne sont plus renvoyées au modèle à chaque échange. Les indicateurs suivis sont le nombre de tokens d'entrée par session, par langue, et le taux de démarches abouties.

## Pièges et limites

- **Croire que le cache réduit Nᵢₙ.** Les tokens sont toujours envoyés, comptés dans la longueur du contexte, et lus par le modèle ; seul leur prix change. Un cache expiré repaie l'écriture, plus chère que le tarif normal.
- **Oublier la sortie.** Fenêtre, résumé et cache n'agissent que sur l'entrée ; un raisonnement long se paie au tarif de sortie, souvent plusieurs fois plus cher.
- **Annoncer « ×4 » pour un contexte doublé.** C'est vrai pour la matrice d'attention, pas pour la facture, qui double.
- **Confondre la borne K(S₀ + MΔ) et la somme exacte.** 60 000 contre 55 000 dans l'exemple : la fenêtre n'est pas pleine au début.
- **Couper sans mesurer ce qu'on perd.** Une fenêtre trop courte ou un top-k trop petit fait sortir du contexte un fait nécessaire ; on garde les faits durables dans une mémoire structurée et l'on mesure le rappel.

### Exercice feuille blanche

1. Sans regarder le code, écrire `total_naif` et `formule_quadratique`, puis vérifier qu'elles donnent 82 500 pour K = 15, S₀ = 2 000 et Δ = 500, et 277 500 pour K = 30.
2. Prédire, puis vérifier : avec une fenêtre M = 2 et les mêmes paramètres, que vaut le total d'entrée sur 15 étapes ? (Réponse : 15 × 2 000 + 500 × 2 × 27/2 = 43 500.)
3. Écrire `plus_petit_K_fenetre_gagne(s0, delta, M, prix_in)` d'après le squelette, avec les formes fermées, et vérifier qu'elle renvoie 55. Puis trouver le bug de cette variante : `prix_prefixe = prix_in * facteur_lecture` pour toutes les étapes, y compris la première. Quel coût d'entrée obtient-on à K = 15, et pourquoi est-il trop optimiste ?

## Pour aller plus loin

Le résumé périodique (tous les M échanges, un sous-agent condense l'historique en R tokens, avec R ≪ MΔ) donne lui aussi un total linéaire en K, au prix d'un appel de résumé à chaque cycle et d'une perte d'information à mesurer. Le calcul d'attention cumulé sur une session naïve, sans cache côté modèle, croît comme la somme des (S₀ + (k − 1)Δ)², c'est-à-dire en K³. Les budgets de contexte et la compaction automatique sont présentés à l'étape 13 ter.

> Suite : [Batching continu et PagedAttention](<72b-Batching-Continu-et-PagedAttention.md>) — étape 72 bis.
