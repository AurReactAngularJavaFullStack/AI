# Palier 11 — Production et coûts

> Palier 11 sur 12 · Précédent : [Palier 10 — Évaluation](<../10-Evaluation/README.md>) · Suivant : [Palier 12 — Assemblage de l'agent complet](<../12-Assemblage-Agent-Complet/README.md>) · Sommaire : [Les douze paliers](<../README.md>) · Leçons à relire : [Étape 66 — Garde-fous, seau à jetons](<../../11-GardeFous/66-GardeFous-Definitions-Fondamentaux.md>) · [Étape 12 — Outils, relances et backoff](<../../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>) · [Étape 68 — Notation de Kendall](<../../12-Production-Couts-Optimisation/68-Notation-de-Kendall.md>) · [Étape 69 — Files d'attente et goulot](<../../12-Production-Couts-Optimisation/69-Files-Attente-et-Goulot.md>) · [Étape 70 — File M/M/1 et p95](<../../12-Production-Couts-Optimisation/70-File-MM1.md>) · [Étape 71 — Erlang C](<../../12-Production-Couts-Optimisation/71-Erlang-C.md>) · [Étape 72 — Coûts et gestion des tokens](<../../12-Production-Couts-Optimisation/72-Couts-et-Gestion-des-Tokens.md>) · [Étape 72 quater — Traces, coûts et percentiles](<../../12-Production-Couts-Optimisation/72d-Observabilite-Traces-Couts-et-Derive.md>) · Démonstrations : [16 — Coût d'inférence](<../../Demonstrations/09-Production/16_cout_inference.md>)

Ce palier est nouveau par rapport à l'agent de l'étape 77 : l'étape 77 s'arrête au moment où la barrière d'intégration continue autorise le déploiement. Ici, on se place juste après. L'agent tourne pour de vrai, et chaque appel au modèle coûte de l'argent, prend du temps et peut échouer. Tu codes les cinq outils qu'une équipe de production utilise tous les jours : le coût d'une tâche en USD et en AED, le seau à jetons qui limite le débit, l'attente exponentielle entre deux relances, le p95 des latences et le budget du jour.

Tous les prix de ce palier sont **illustratifs** : 3 USD par million de tokens d'entrée, 15 USD par million de tokens de sortie, un token relu dans le cache à 0,1 fois le prix d'entrée et un token écrit dans le cache à 1,25 fois ce prix, comme à l'étape 72. On les vérifie sur la grille du fournisseur et du modèle choisis avant tout chiffrage réel. Seule la parité de 3,6725 AED pour 1 USD est un chiffre réel.

## Où en est l'agent

Les paliers 01 à 10 ont construit l'agent : le prompt et le faux modèle (01), la validation (02), les calculs EAU (03), le registre d'outils (04), la boucle ReAct (05), la mémoire (06), la recherche hybride (07), la planification (08), les garde-fous (09) et l'évaluation (10). Le module de ce palier ne touche à aucun d'eux : il se place **autour** de l'appel au modèle.

```text
                         question du client C-1
                                   │
  ┌────────────────────────────────▼─────────────────────────────────────────┐
  │ 01 prompt ──► 05 boucle ReAct ──► 04 registre ──► 03 outils EAU          │
  │  ▲ 06 mémoire      │      ▲        ▲ 02 schémas    09 garde-fous         │
  │  ▲ 07 recherche    │      │ tool_result                                  │
  │                    ▼      │                                              │
  │   ╔════════════════════════════════════════════════════════════════╗     │
  │   ║ 11 PRODUCTION  (ce palier)                                     ║     │
  │   ║  avant l'appel : SeauAJetons.consommer → assez de débit ?      ║     │
  │   ║  l'appel       : executer_avec_relances → 429 / 529 relancés   ║     │
  │   ║  après l'appel : cout_tache → budget_restant ; latence → p95   ║     │
  │   ╚════════════════════════════════════════════════════════════════╝     │
  │                    port LLM : create(system, messages, tools)            │
  └──────────────────────────────────────────────────────────────────────────┘
     10 évaluation : avant le déploiement     08 planification : à part
```

Dans la boucle percevoir → décider → agir → observer, c'est l'étape « décider » qui appelle le modèle, et c'est elle qui coûte : chaque tour renvoie le prompt système, les définitions d'outils et tout l'historique (étape 72). Le seau à jetons décide si l'appel peut partir maintenant, les relances absorbent les surcharges passagères du fournisseur, le coût de chaque tâche est retiré du budget du jour, et la latence de chaque tâche alimente le p95 que l'on compare au contrat de service. Sans ce module, un agent correct peut quand même ruiner son budget en une nuit, ou laisser une requête sur vingt attendre dix secondes sans que personne ne le voie.

## Ce que tu vas coder

Dans `projet/agent/production.py` :

- `cout_tache` rend le coût d'une tâche en USD et en AED, à partir des tokens d'entrée, de sortie, lus dans le cache et écrits dans le cache.
- `SeauAJetons` est un seau de capacité C qui se remplit de r jetons par seconde (horloge simulée) et refuse une demande trop grosse sans rien retirer.
- `attente_backoff` rend l'attente avant la relance numéro k : une exponentielle de base 2, plafonnée, raccourcie par une gigue tirée d'un générateur local.
- `ErreurTransitoire` est l'exception qui mérite une relance (surcharge, limite de débit, coupure réseau) ; elle est déjà écrite.
- `executer_avec_relances` appelle une fonction, relance après chaque `ErreurTransitoire` en avançant l'horloge, et laisse remonter toute autre exception.
- `percentile` rend le percentile au rang le plus proche, et `p95` le 95e.
- `budget_restant` rend le budget moins les dépenses, négatif en cas de dépassement, et `taches_possibles` le nombre de tâches encore finançables.

Les quatre constantes `PRIX_ENTREE_USD_MTOK`, `PRIX_SORTIE_USD_MTOK`, `FACTEUR_LECTURE_CACHE` et `FACTEUR_ECRITURE_CACHE` sont fournies.

## Rappel de cours

**Le coût d'une tâche (étapes 72 et 72 quater).** Le fournisseur facture séparément les tokens d'entrée non mis en cache, les tokens relus dans le cache, les tokens écrits dans le cache et les tokens de sortie. Les prix sont donnés en USD par million de tokens :

$$
\text{Coût}_{USD} = \frac{N_{in}\,P_{in} + f\,N_{\text{lu}}\,P_{in} + w\,N_{\text{écrit}}\,P_{in} + N_{out}\,P_{out}}{10^6}
$$

$$
\text{Coût}_{AED} = 3{,}6725 \times \text{Coût}_{USD}
$$

**Le seau à jetons (étape 66).** Avant chaque demande, le seau se recharge pour le temps écoulé, sans dépasser sa capacité ; la demande passe si elle tient dans le seau :

$$
j \leftarrow \min\bigl(C,\; j + r\,(t - t_d)\bigr)
$$

$$
\text{la demande } c \text{ passe} \iff c \le j \qquad \text{et alors} \qquad j \leftarrow j - c
$$

Sur toute fenêtre de durée T, ce qui passe est borné :

$$
J(t_0,\; t_0 + T) \le C + r\,T
$$

**L'attente exponentielle avec gigue (étape 12).** Avant la relance numéro k, on attend :

$$
a_k = \min\bigl(a_{max},\; b \cdot 2^{k-1}\bigr) \cdot (1 - g\,u) \qquad u \in [0\,;\,1)
$$

**Le percentile au rang le plus proche (étapes 70 et 72 quater).** Sur n valeurs triées par ordre croissant, le percentile d'ordre p est une valeur observée, celle de rang :

$$
P_p = x_{(k)} \qquad k = \left\lceil \frac{p\,n}{100} \right\rceil
$$

**Le budget.** On retire les dépenses du budget, puis on compte les tâches encore finançables :

$$
\text{reste} = B - \sum_{i} d_i \qquad \text{tâches} = \max\left(0,\; \left\lfloor \frac{\text{reste}}{c_t} \right\rfloor\right)
$$

### Les symboles, un par un

$$
N_{in}
$$

Nombre de tokens d'entrée **hors cache** d'une tâche (la question, les résultats d'outils, ce qui change à chaque tour) ; paramètre `tokens_entree`.

$$
N_{\text{lu}}
$$

Nombre de tokens relus dans le cache : un préfixe déjà envoyé, identique au token près ; paramètre `cache_lus`.

$$
N_{\text{écrit}}
$$

Nombre de tokens écrits dans le cache, la première fois que le préfixe est envoyé ; paramètre `cache_ecrits`.

$$
N_{out}
$$

Nombre de tokens générés par le modèle ; ils ne se mettent jamais en cache ; paramètre `tokens_sortie`.

$$
P_{in}
$$

Prix d'entrée, en USD par million de tokens : 3 ici, illustratif ; constante `PRIX_ENTREE_USD_MTOK`.

$$
P_{out}
$$

Prix de sortie, en USD par million de tokens : 15 ici, cinq fois le prix d'entrée, illustratif ; constante `PRIX_SORTIE_USD_MTOK`.

$$
f
$$

Facteur de prix d'un token relu dans le cache, en fraction du prix d'entrée : 0,1 ; constante `FACTEUR_LECTURE_CACHE`.

$$
w
$$

Facteur de prix d'un token écrit dans le cache, en multiple du prix d'entrée : 1,25 ; constante `FACTEUR_ECRITURE_CACHE`.

$$
C
$$

Capacité du seau, en jetons : la plus grosse rafale qu'il laisse passer d'un coup ; attribut `capacite`.

$$
r
$$

Recharge du seau, en jetons par seconde : le débit moyen qu'il tolère sur la durée ; attribut `recharge`.

$$
j
$$

Jetons présents dans le seau, un réel entre 0 et C ; attribut `jetons`.

$$
t_d
$$

Instant (secondes simulées) de la dernière mise à jour du seau ; attribut `dernier`.

$$
c
$$

Coût d'une demande, en jetons, par exemple les tokens qu'un appel au modèle va consommer ; paramètre `cout` de `consommer`.

$$
J(t_0,\; t_0 + T)
$$

Total des jetons consommés par les demandes acceptées entre les instants t₀ et t₀ + T.

$$
a_k
$$

Attente, en secondes, avant la relance numéro k ; valeur rendue par `attente_backoff`.

$$
k
$$

Numéro de la relance, à partir de 1 ; paramètre `tentative`. Dans le percentile, k désigne le rang.

$$
b
$$

Attente de base, en secondes, celle de la première relance ; paramètre `base_s`.

$$
a_{max}
$$

Plafond de l'attente, en secondes ; paramètre `plafond_s`.

$$
g
$$

Gigue, la fraction maximale de l'attente que l'on retire au hasard, entre 0 et 1 ; paramètre `gigue`.

$$
u
$$

Tirage uniforme dans [0 ; 1), donné par `rng.random()` d'un `random.Random` local.

$$
p
$$

Ordre du percentile, en pour cent, dans ]0 ; 100] : 95 pour le p95, 50 pour la médiane.

$$
n
$$

Nombre de valeurs mesurées, par exemple 20 latences.

$$
x_{(k)}
$$

La k-ième plus petite valeur : x₍₁₎ est le minimum, x₍ₙ₎ le maximum.

$$
B
$$

Budget, en AED, par exemple le budget du jour ; paramètre `budget_aed`.

$$
d_i
$$

Dépense numéro i, en AED ; éléments de la liste `depenses_aed`.

$$
c_t
$$

Coût d'une tâche, en AED ; paramètre `cout_tache_aed`.

**Le cache est rentable dès la première relecture.** Un préfixe de S tokens est envoyé k + 1 fois au cours d'une tâche. Sans cache, il coûte (k + 1) S P_in ; avec cache, il est écrit une fois puis relu k fois. Le cache coûte moins cher si et seulement si :

$$
w + k\,f < k + 1 \iff k\,(1 - f) > w - 1 \iff k > \frac{w - 1}{1 - f} = \frac{0{,}25}{0{,}9} \approx 0{,}28
$$

La première équivalence regroupe les termes en k d'un côté ; la seconde divise par 1 − f = 0,9, qui est positif, ce qui garde le sens de l'inégalité. Une seule relecture (k = 1) suffit donc. Sur l'exemple de la spécification, le préfixe de 4 000 tokens envoyé trois fois coûte 12 000 × 3 / 10⁶ = 0,036 USD sans cache et (4 000 × 1,25 + 8 000 × 0,1) × 3 / 10⁶ = 0,0174 USD avec : c'est exactement l'écart entre 0,057 USD et 0,0384 USD. Le cache ne retire aucun token, il en change le prix (étape 72, point 4).

**Le seau ne laisse jamais passer plus de C + r T.** Sur la fenêtre, chaque jeton consommé était soit dans le seau au départ, soit ajouté par la recharge ; ceux qui restent à la fin n'ont pas été consommés. Donc J = j(t₀) + recharge effective − j(t₀ + T). Or j(t₀) ≤ C parce que le seau ne déborde jamais, la recharge effective est au plus r T parce que le `min` ne peut qu'en retirer, et j(t₀ + T) ≥ 0. D'où J ≤ C + r T (étape 66, point 6). Le seau tolère une rafale de C, mais pas un débit soutenu supérieur à r.

**Le total des attentes double à chaque relance.** Sans plafond ni gigue, K relances attendent au total :

$$
\sum_{k=1}^{K} b \cdot 2^{k-1} = b\,(2^K - 1)
$$

C'est une somme géométrique de raison 2 : multiplier la somme par 2 la décale d'un rang, et la différence des deux ne garde que b 2ᴷ − b. Avec b = 1 s, trois relances attendent 1 + 2 + 4 = 7 = 2³ − 1 secondes. La gigue multiplie l'attente par 1 − g u, un nombre de ]1 − g ; 1] : elle ne peut que la raccourcir, donc le plafond a_max tient toujours.

**Le rang du percentile est toujours valide.** Si 0 < p ≤ 100, alors 0 < p n / 100 ≤ n, et le plafond d'un nombre de ]0 ; n] est un entier de 1 à n : le rang désigne toujours une valeur de la liste. C'est pour cela que p = 0 est refusé (il donnerait le rang 0, qui n'existe pas). Et au moins p % des valeurs sont inférieures ou égales à P_p : les k premières le sont, et k ≥ p n / 100.

## Spécification

### cout_tache

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`cout_tache(tokens_entree, tokens_sortie, cache_lus, cache_ecrits, prix_entree, prix_sortie)`** — Cette fonction doit faire le travail d'un caissier qui facture quatre sortes de marchandises à quatre tarifs différents, puis convertit l'addition en dirhams. Elle reçoit les tokens d'entrée hors cache, les tokens de sortie, les tokens relus et écrits dans le cache, nuls par défaut, et les deux prix en USD par million, 3 et 15 par défaut ; elle doit lever `ValueError` pour un nombre de tokens ou un prix négatif. Sinon, elle facture les relus à 0,1 fois le prix d'entrée et les écrits à 1,25 fois ce prix, divise le total par 10⁶ et rend `{"usd": …, "aed": …}` sans arrondi, l'AED valant 3,6725 fois l'USD : 0,0384 USD et 0,141024 AED pour la tâche à trois appels de l'exemple.

```python
# [extrait] spécification
def cout_tache(tokens_entree: int, tokens_sortie: int, cache_lus: int = 0, cache_ecrits: int = 0,
               prix_entree: float = PRIX_ENTREE_USD_MTOK, prix_sortie: float = PRIX_SORTIE_USD_MTOK) -> dict:
    ...
```

Rend `{"usd": …, "aed": …}`, sans arrondi. `tokens_entree` ne compte que les tokens d'entrée hors cache ; les tokens lus et écrits dans le cache sont facturés au prix d'**entrée** multiplié par leur facteur ; la sortie ne se met jamais en cache. Les prix sont en USD par million de tokens, d'où la division par 10⁶. Un nombre de tokens négatif ou un prix négatif lève `ValueError`. Zéro token est permis, et coûte 0.

**Exemple chiffré.** Une tâche de trois appels au modèle. Le préfixe de 4 000 tokens (prompt système et définitions d'outils) est écrit dans le cache au premier appel, puis relu aux deux suivants, soit 8 000 tokens lus ; les parties qui changent à chaque appel font 2 000 tokens d'entrée hors cache ; le modèle écrit 1 000 tokens en tout.

$$
\frac{2\,000 \times 3 + 4\,000 \times 1{,}25 \times 3 + 8\,000 \times 0{,}1 \times 3 + 1\,000 \times 15}{10^6} = \frac{6\,000 + 15\,000 + 2\,400 + 15\,000}{10^6} = 0{,}0384 \text{ USD}
$$

En AED : 0,0384 × 3,6725 = 0,141024 AED. Sans cache, les mêmes 14 000 tokens d'entrée coûtent (14 000 × 3 + 1 000 × 15) / 10⁶ = 0,057 USD, soit 0,2093325 AED. Pour 10 000 tokens d'entrée seuls : 0,03 USD au tarif plein, 0,003 USD relus dans le cache (× 0,1), 0,0375 USD écrits dans le cache (× 1,25). Tests : `TestCout.test_exemple_avec_cache`, `TestCout.test_lecture_du_cache_au_dixieme`, `TestCout.test_entrees_invalides`.

### SeauAJetons

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`SeauAJetons.__init__(capacite, recharge_par_s, horloge)`** — Le constructeur doit installer une citerne posée sous un robinet qui goutte à débit constant, et la livrer pleine. Il reçoit la capacité C en jetons, la recharge r en jetons par seconde et l'horloge simulée ; il lève `ValueError` pour une capacité nulle ou négative et pour une recharge négative, mais accepte une recharge nulle, celle d'un seau qui ne se remplit plus. Il range `capacite`, `recharge` et `horloge`, met `jetons` à `float(capacite)` et note dans `dernier` l'instant courant de l'horloge ; il ne rend rien, et prépare l'état minimal, deux nombres, dont la consommation aura besoin.

**`SeauAJetons.consommer(cout)`** — Cette méthode est le geste de celui qui vient puiser à la citerne : il regarde d'abord combien d'eau s'est accumulée depuis son dernier passage, puis ne remplit son seau que s'il y a assez. Elle reçoit le coût de la demande, lève `ValueError` s'il est négatif, ajoute r fois le temps écoulé depuis `dernier` sans dépasser la capacité, remet `dernier` à l'heure, puis retire le coût et rend `True` si `cout <= jetons`, ou rend `False` sans rien retirer dans le cas contraire. Avec C = 10 000, r = 50 et des appels de 3 000, la séquence attendue est trois acceptations, un refus à 1 000 jetons, une acceptation à 40 s quand le seau est remonté à 3 000, puis un dernier refus.

```python
# [extrait] spécification
class SeauAJetons:
    def __init__(self, capacite: float, recharge_par_s: float, horloge: Horloge) -> None: ...
    def consommer(self, cout: float) -> bool: ...
```

Le constructeur refuse une capacité nulle ou négative et une recharge négative (`ValueError`) ; une recharge nulle est permise (un seau qui ne se remplit plus). Il garde `capacite`, `recharge` et `horloge`, démarre **plein** (`jetons` vaut `float(capacite)`) et note dans `dernier` l'instant de l'horloge. `consommer(cout)` refuse un coût négatif, recharge le seau pour le temps écoulé depuis `dernier` en plafonnant à la capacité, met `dernier` à l'heure, puis accepte la demande si `cout <= jetons` (elle retire alors le coût et rend `True`) ; sinon elle rend `False` **sans rien retirer**. Le seau ne lit jamais l'heure réelle : seule l'`Horloge` simulée avance.

**Exemple chiffré (étape 66).** C = 10 000 tokens, r = 50 tokens par seconde, des appels de 3 000 tokens.

| Instant | Jetons avant | Demande | Décision | Jetons après |
| --- | --- | --- | --- | --- |
| 0 s | 10 000 | 3 000 | acceptée | 7 000 |
| 0 s | 7 000 | 3 000 | acceptée | 4 000 |
| 0 s | 4 000 | 3 000 | acceptée | 1 000 |
| 0 s | 1 000 | 3 000 | refusée | 1 000 |
| 40 s | 1 000 + 50 × 40 = 3 000 | 3 000 | acceptée | 0 |
| 40 s | 0 | 3 000 | refusée | 0 |

Sur [0 ; 40], le seau a laissé passer 4 × 3 000 = 12 000 tokens, exactement C + r T = 10 000 + 50 × 40 : la borne est atteinte. Second cas : après une demande de 9 000 tokens (il en reste 1 000), on avance de 1 000 s ; la recharge donnerait 1 000 + 50 000, plafonnée à 10 000 ; `consommer(0)` rend `True` et laisse 10 000 jetons, `consommer(10_001)` rend `False`. Tests : `TestSeauAJetons.test_sequence_de_l_etape_66`, `TestSeauAJetons.test_recharge_plafonnee`, `TestSeauAJetons.test_entrees_invalides`.

### attente_backoff

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`attente_backoff(tentative, base_s, plafond_s, gigue, rng)`** — Cette fonction doit raisonner comme quelqu'un qui frappe à une porte close et double sa patience à chaque essai, sans jamais attendre plus qu'un plafond raisonnable, en variant un peu l'instant pour ne pas frapper en même temps que ses voisins. Elle reçoit le numéro de la relance, l'attente de base, 1 s par défaut, le plafond, 30 s, la gigue, nulle par défaut, et un générateur `rng` facultatif ; elle lève `ValueError` si la tentative vaut moins de 1, si la base est nulle ou négative, si le plafond est sous la base ou si la gigue sort de [0 ; 1]. Elle rend min(plafond, base × 2ᵏ⁻¹), multiplié par 1 − g × u seulement si un générateur est fourni et que la gigue est positive : 1, 2, 4, 8, 16, puis 30 et 30 s pour les tentatives 1 à 7 sans gigue.

```python
# [extrait] spécification
def attente_backoff(tentative: int, base_s: float = 1.0, plafond_s: float = 30.0, gigue: float = 0.0,
                    rng: random.Random | None = None) -> float:
    ...
```

Rend l'attente, en secondes, avant la relance numéro `tentative`. L'attente nominale est `min(plafond_s, base_s * 2 ** (tentative - 1))`. Si un générateur `rng` est fourni **et** que la gigue est strictement positive, on la multiplie par `1 - gigue * rng.random()` ; sinon pas de gigue. Erreurs (`ValueError`) : `tentative < 1` ; `base_s <= 0` ; `plafond_s < base_s` ; une gigue hors de [0 ; 1].

**Exemple chiffré.** Avec b = 1 s et un plafond de 30 s, les tentatives 1 à 7 attendent 1, 2, 4, 8, 16, puis min(30 ; 32) = 30 et min(30 ; 64) = 30 secondes. Avec une gigue g = 0,5 et u = 0,4, la troisième attente vaudrait 4 × (1 − 0,5 × 0,4) = 4 × 0,8 = 3,2 s. Avec le générateur `random.Random(3)`, le premier tirage vaut u = 0,237965 (à 10⁻⁶ près), donc a₃ = 4 × (1 − 0,5 × 0,237965) = 4 × 0,881018 = 3,524071 s, bien dans ]2 ; 4]. Tests : `TestBackoff.test_exponentielle_plafonnee`, `TestBackoff.test_gigue_tiree_d_un_generateur_local`, `TestBackoff.test_entrees_invalides` (tentative 0, base 0, plafond 0,5 sous la base 1, gigue 1,5).

### ErreurTransitoire et executer_avec_relances

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_avec_relances(fonction, max_tentatives, base_s, plafond_s, gigue, graine, horloge)`** — On attend de cette fonction l'obstination raisonnée d'un standardiste qui rappelle un correspondant occupé, en notant chaque échec et chaque pause, mais qui raccroche aussitôt si on lui répond que le numéro n'existe pas. Elle reçoit la fonction à appeler sans argument, le nombre maximal de tentatives, 4 par défaut, les paramètres du backoff, une graine et une horloge facultative ; elle lève `ValueError` si `max_tentatives` vaut moins de 1, crée un seul générateur local `random.Random(graine)`, puis appelle la fonction au plus `max_tentatives` fois. Après chaque `ErreurTransitoire`, elle note le message et, s'il reste une tentative, calcule l'attente avec `attente_backoff`, la note et avance l'horloge ; toute autre exception remonte sans relance. Elle rend un dictionnaire `statut`, `resultat`, `tentatives`, `attentes`, `erreurs` : « succes » en 3 tentatives avec les attentes [1, 2] pour deux surcharges sans gigue, « echec » avec 4 erreurs et 3 attentes pour une panne permanente.

```python
# [extrait] spécification
class ErreurTransitoire(Exception): ...

def executer_avec_relances(fonction, max_tentatives: int = 4, base_s: float = 1.0, plafond_s: float = 30.0,
                           gigue: float = 0.1, graine: int = 0, horloge: Horloge | None = None) -> dict:
    ...
```

`ErreurTransitoire` est fournie. `executer_avec_relances` refuse `max_tentatives < 1`, crée **un** générateur `random.Random(graine)` local, puis appelle `fonction()` au plus `max_tentatives` fois. Un succès rend aussitôt `{"statut": "succes", "resultat": …, "tentatives": numéro de la tentative réussie, "attentes": […], "erreurs": […]}`. Une `ErreurTransitoire` est notée dans `erreurs` (son message) ; s'il reste une tentative, l'attente `attente_backoff(tentative, base_s, plafond_s, gigue, rng)` est notée dans `attentes` et l'horloge avance d'autant (si elle est fournie). Il n'y a pas d'attente après la dernière tentative ratée. Après la dernière, la fonction rend `{"statut": "echec", "resultat": None, "tentatives": max_tentatives, …}`. **Toute autre exception remonte aussitôt**, sans relance : une requête invalide (400) ou un refus de politique ne se corrigent pas en réessayant.

**Exemple chiffré.** Une fonction échoue deux fois par `ErreurTransitoire("surcharge (529)")`, puis rend "réponse". Sans gigue : la tentative 1 échoue, on attend 1 s ; la tentative 2 échoue, on attend 2 s ; la tentative 3 réussit. Résultat : statut "succes", 3 tentatives, attentes [1, 2], horloge avancée de 1 + 2 = 3 s, fonction appelée 3 fois. Une fonction qui échoue toujours, avec `max_tentatives=4` : 4 erreurs, 3 attentes seulement, statut "echec", et deux exécutions avec la même graine donnent les mêmes attentes. Une fonction qui lève `ValueError("400 : requête invalide")` est appelée une seule fois, et l'erreur remonte. Tests : `TestRelances.test_succes_apres_deux_echecs`, `TestRelances.test_echec_apres_max_tentatives_et_determinisme`, `TestRelances.test_erreur_non_transitoire_remonte_aussitot`.

### percentile et p95

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`percentile(valeurs, p)`** — Cette fonction doit se comporter comme un chef de course qui aligne les coureurs par temps d'arrivée et désigne celui qui occupe un rang précis de la file, sans jamais inventer un temps intermédiaire. Elle reçoit une liste de valeurs et un ordre p en pour cent ; elle lève `ValueError` si la liste est vide ou si p sort de ]0 ; 100], trie une copie des valeurs, calcule le rang ⌈p × n / 100⌉ en multipliant avant de diviser, et rend la valeur de ce rang, à l'indice rang − 1. Sur les 20 latences de 1,0 à 2,9 s, elle doit rendre 1,9 s pour p = 50 et 2,8 s pour p = 95, et 7 et non 8 pour les entiers de 1 à 100 avec p = 7.

**`p95(valeurs)`** — Cette petite fonction est le raccourci du tableau de bord, le cadran unique que l'équipe d'astreinte regarde avant tout autre. Elle reçoit une liste de latences et doit rendre simplement `percentile(valeurs, 95)`, en héritant de toutes ses vérifications, donc de la même `ValueError` pour une liste vide. Pour les 20 latences de l'exemple, elle rend 2,8 s, et pour une seule latence de 0,7 s, dont le rang vaut ⌈0,95⌉ = 1, elle rend 0,7 s : c'est ce nombre, et non la moyenne, que l'on compare au contrat de service.

```python
# [extrait] spécification
def percentile(valeurs: list[float], p: float) -> float: ...

def p95(valeurs: list[float]) -> float: ...
```

`percentile` trie une copie des valeurs, calcule le rang `math.ceil(p * n / 100)` et rend la valeur de ce rang (indice `rang - 1` en Python). C'est toujours une valeur observée, jamais une interpolation. On **multiplie avant de diviser** : en flottant, `7 / 100 * 100` vaut 7.000000000000001 et son plafond 8, alors que `7 * 100 / 100` vaut exactement 7. Une liste vide ou un p hors de ]0 ; 100] lève `ValueError`. `p95(valeurs)` vaut `percentile(valeurs, 95)`.

**Exemple chiffré.** Les 20 latences 1,0 ; 1,1 ; … ; 2,9 s (pas de 0,1). Rang du p95 : ⌈95 × 20 / 100⌉ = ⌈19⌉ = 19, et la 19e plus petite vaut 1,0 + 18 × 0,1 = 2,8 s. Rang de la médiane : ⌈50 × 20 / 100⌉ = 10, soit 1,9 s. L'ordre de la liste ne change rien (la liste renversée donne aussi 2,8 s). Une seule latence de 0,7 s : rang ⌈0,95⌉ = 1, p95 = 0,7 s. Les entiers de 1 à 100, p = 7 : rang 7, valeur 7 (et non 8). Tests : `TestPercentilesEtBudget.test_p95_au_rang_le_plus_proche`.

### budget_restant et taches_possibles

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`budget_restant(budget_aed, depenses_aed)`** — Cette fonction doit tenir le carnet d'un trésorier honnête, qui écrit le solde en rouge plutôt que de l'effacer quand on a trop dépensé. Elle reçoit le budget en AED et la liste des dépenses ; elle lève `ValueError` si le budget ou l'une des dépenses est négatif, puis rend le budget moins la somme des dépenses, sans le ramener à zéro. Pour un budget de 50 AED et des dépenses de 12,5, 20,25 et 7,0 AED, elle rend 10,25 AED, et pour un budget de 10 AED et une dépense de 12 AED, elle rend −2 AED : un dépassement doit rester visible.

**`taches_possibles(reste_aed, cout_tache_aed)`** — Celle-ci est le même trésorier qui se demande combien de commandes il peut encore régler en entier, sans compter celle qu'il ne pourrait payer qu'à moitié. Elle reçoit le reste en AED et le coût d'une tâche ; elle lève `ValueError` pour un coût nul ou négatif, puis rend la partie entière inférieure du quotient, ou 0 si le reste est négatif ou nul. Avec 10,25 AED et 0,141024 AED par tâche, le quotient vaut 72,68…, et elle rend 72, car 73 tâches coûteraient 10,294752 AED, plus que ce qui reste.

```python
# [extrait] spécification
def budget_restant(budget_aed: float, depenses_aed: list[float]) -> float: ...

def taches_possibles(reste_aed: float, cout_tache_aed: float) -> int: ...
```

`budget_restant` refuse un budget ou une dépense négatifs, puis rend `budget_aed - sum(depenses_aed)`, **négatif** en cas de dépassement : ramener un dépassement à 0 le cacherait. `taches_possibles` refuse un coût de tâche nul ou négatif, puis rend la partie entière inférieure du quotient, et 0 si le reste est négatif ou nul.

**Exemple chiffré.** Budget du jour de 50 AED, dépenses de 12,5, 20,25 et 7,0 AED : 50 − 39,75 = 10,25 AED. Avec 0,141024 AED par tâche (le coût avec cache ci-dessus) : 10,25 / 0,141024 = 72,68…, donc 72 tâches ; en effet 72 × 0,141024 = 10,153728 ≤ 10,25 < 73 × 0,141024 = 10,294752. Arrondir au plus proche donnerait 73, une tâche qu'on ne peut pas payer. Un budget de 10 AED et une dépense de 12 AED donnent −2 AED, et 0 tâche possible. Tests : `TestPercentilesEtBudget.test_budget`.

## Squelette algorithmique

```text
ALGORITHME CoûtTâche
ENTRÉES : tokens d'entrée hors cache, de sortie, lus, écrits ; prix d'entrée et de sortie (USD par million)
SORTIE  : coût en USD et en AED
  SI un nombre de tokens < 0 OU un prix < 0 ALORS ERREUR
  usd ← (entrée × Pin + lus × 0,1 × Pin + écrits × 1,25 × Pin + sortie × Pout) / 1 000 000
  RETOURNER (usd, usd × 3,6725)

ALGORITHME SeauConsommer(seau, c)
  SI c < 0 ALORS ERREUR
  seau.jetons ← min(C, seau.jetons + r × (maintenant − seau.dernier))
  seau.dernier ← maintenant
  SI c ≤ seau.jetons ALORS seau.jetons ← seau.jetons − c ; RETOURNER vrai
  RETOURNER faux                                         (le seau ne change pas)

ALGORITHME AttenteBackoff(k, b, amax, g, générateur)
  a ← min(amax, b × 2 puissance (k − 1))
  SI générateur fourni ET g > 0 ALORS a ← a × (1 − g × tirage dans [0 ; 1))
  RETOURNER a

ALGORITHME ExécuterAvecRelances(f, K, graine, horloge)
  générateur ← nouveau générateur(graine) ; attentes ← [] ; erreurs ← []
  POUR k DE 1 À K FAIRE
      ESSAYER : RETOURNER (succès, f(), k, attentes, erreurs)
      SAUF ErreurTransitoire e :
          ajouter e à erreurs
          SI k < K ALORS a ← AttenteBackoff(k, …, générateur) ; ajouter a à attentes ; avancer horloge de a
      (toute autre erreur remonte sans relance)
  FIN POUR
  RETOURNER (échec, rien, K, attentes, erreurs)

ALGORITHME Percentile(valeurs, p)
  SI valeurs vide OU p hors de ]0 ; 100] ALORS ERREUR
  triées ← copie triée de valeurs ; n ← taille
  rang ← plafond(p × n / 100)                            (multiplier avant de diviser)
  RETOURNER triées[rang]                                 (rang compté à partir de 1)

ALGORITHME Budget(B, dépenses, coût)
  reste ← B − somme des dépenses                         (négatif si dépassement)
  RETOURNER reste, max(0, partie entière inférieure de reste / coût)
```

**Complexité.** Le coût, la consommation du seau, l'attente et le budget se calculent en temps constant, sauf la somme des dépenses, linéaire en leur nombre. Le seau garde deux nombres en mémoire, jamais l'historique des demandes : c'est ce qui le rend utilisable devant chaque appel. Les relances font au plus K appels à la fonction et K − 1 attentes, et l'attente totale est bornée par K − 1 fois le plafond. Le percentile trie une copie : O(n log n) en temps et O(n) en mémoire ; pour suivre un p95 en continu sur des millions de requêtes, on garde des histogrammes par tranches au lieu de toutes les valeurs (étape 72 quater).

**Du squelette au code.** `CoûtTâche` est `cout_tache`, avec les constantes `PRIX_ENTREE_USD_MTOK`, `PRIX_SORTIE_USD_MTOK`, `FACTEUR_LECTURE_CACHE` et `FACTEUR_ECRITURE_CACHE`, et la parité `AED_PAR_USD` du palier 03. `SeauConsommer` est la méthode `consommer` de `SeauAJetons`, dont le constructeur crée les attributs `jetons` et `dernier`. `AttenteBackoff` est `attente_backoff`, `ExécuterAvecRelances` est `executer_avec_relances`, qui n'attrape que `ErreurTransitoire`. `Percentile` est `percentile`, que `p95` appelle avec p = 95, et `Budget` se répartit entre `budget_restant` et `taches_possibles`. « maintenant » est l'attribut `t` de l'`Horloge` du palier 01.

## Cas d'usage aux Émirats

Les volumes, budgets, capacités et prix ci-dessous sont illustratifs ; seule la parité de 3,6725 AED pour 1 USD est réelle.

**Banque — le budget du jour de l'assistant de la banque B-1 (Dubaï).** L'assistant traite 40 000 demandes par jour, chacune de la forme de l'exemple : trois appels, 14 000 tokens d'entrée, 1 000 de sortie. Sans cache, la journée coûte 40 000 × 0,2093325 = 8 373,30 AED ; avec le préfixe de 4 000 tokens mis en cache, 40 000 × 0,141024 = 5 640,96 AED, soit 2 732,34 AED économisés par jour sans changer une seule réponse. L'équipe fixe un budget du jour et appelle `budget_restant` après chaque tâche ; quand `taches_possibles` tombe sous le nombre de demandes attendues avant minuit, l'agent bascule sur des réponses plus courtes ou passe la main à un conseiller, au lieu de découvrir le dépassement sur la facture du mois. Le préfixe doit rester identique au token près : une date ou un identifiant de session placé dans le prompt système casserait le cache à chaque appel, et la facture remonterait à 8 373,30 AED sans aucune erreur visible.

**Crypto — un débit borné et des relances désynchronisées sur une plateforme agréée par la VARA.** L'agent de support interroge un fournisseur de données de marché qui facture à l'appel. Un seau de C = 20 appels, rechargé de r = 0,5 appel par seconde, protège ce fournisseur : si une boucle emballée envoie 100 appels en 10 secondes, au plus 20 + 0,5 × 10 = 25 passent, et les 75 autres sont refusés avant de coûter. Lors d'un pic, 500 sessions reçoivent en même temps une erreur 529 du modèle. Sans gigue, elles relancent toutes exactement à 1 s, puis à 2 s, puis à 4 s, et recréent le pic à chaque fois. Avec g = 0,5, la troisième relance de chacune tombe quelque part dans ]2 ; 4] secondes, et le fournisseur voit une charge étalée.

**Secteur public — un contrat de service sur le p95, pas sur la moyenne.** Une entité de services publics en ligne promet que 95 % des réponses de son assistant arrivent en moins de 3 secondes. Sur 20 sessions mesurées (les latences de `demo.py`), la moyenne vaut 35,5 / 20 = 1,775 s et la médiane 1,4 s : tout semble aller bien. Mais le rang du p95 est ⌈95 × 20 / 100⌉ = 19, et la 19e latence vaut 3,4 s : le contrat n'est pas tenu, parce qu'une session sur vingt attend plus du double de la médiane. C'est la file d'attente des étapes 69 et 70 qui explique cette queue, et c'est le p95 qui la rend visible ; l'alerte se règle sur `p95(latences) > 3.0`, jamais sur la moyenne.

## Travail à faire

Toutes les commandes se lancent dans PowerShell, depuis `projet/`. Si `python` n'est pas dans le PATH, remplace-le par `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.

1. Lire ce README en entier, puis refaire sur une feuille A4 les exemples chiffrés de la spécification : 0,0384 USD, la table du seau, les attentes 1, 2, 4, 8, 16, 30, 30, le rang 19 du p95 et les 72 tâches.
2. Se placer dans le projet et vérifier le point de départ : les 136 tests des paliers 01 à 10 passent, les 14 tests du palier 11 échouent tous par `NotImplementedError`.

```text
cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\11-Production-et-Couts\projet"
python -m unittest
```

3. Ouvrir `agent/production.py`. Coder `cout_tache`, puis lancer `python -m unittest -v tests.test_11_production.TestCout`.
4. Coder le constructeur et `consommer` de `SeauAJetons`, puis lancer `python -m unittest -v tests.test_11_production.TestSeauAJetons`.
5. Coder `attente_backoff`, puis lancer `python -m unittest -v tests.test_11_production.TestBackoff`.
6. Coder `executer_avec_relances`, puis lancer `python -m unittest -v tests.test_11_production.TestRelances`.
7. Coder `percentile`, `p95`, `budget_restant` et `taches_possibles`, puis lancer `python -m unittest -v tests.test_11_production.TestPercentilesEtBudget`.
8. Lancer tous les tests, puis la démo, et comparer sa sortie à celle ci-dessous.

```text
python -m unittest -v
python demo.py
```

## Critères de réussite

- `python -m unittest` affiche `Ran 150 tests` puis `OK` : les 136 tests des paliers précédents et les 14 du palier 11.
- `python demo.py` affiche exactement la sortie ci-dessous, à chaque exécution : aucune horloge réelle, aucun hasard global.
- Tu sais expliquer pourquoi le cache est rentable dès la première relecture, pourquoi le seau ne laisse jamais passer plus de C + r T, et pourquoi la moyenne des latences ne dit rien du p95.

### Sortie attendue de demo.py

```text
Palier 11 — l'agent de la banque B-1 en production (prix illustratifs : 3 et 15 USD par million)
1. Une tâche, 14 000 tokens d'entrée sans cache : 0.0570 USD = 0.209333 AED
   avec 4 000 écrits et 8 000 relus dans le cache : 0.0384 USD = 0.141024 AED
2. Budget journalier 50 AED, déjà dépensé 39,75 AED : reste 10.25 AED, soit 72 tâches
3. Seau de 10 000 tokens, recharge 50/s, appels de 3 000 : [True, True, True, False, True, False] (deux derniers à t = 40 s)
4. Trois surcharges puis succès : succes en 4 tentatives ; attentes 0.910, 1.776, 3.261 s ; horloge +5.946 s
   panne longue : echec après 3 tentatives, attentes [1.0, 2.0]
5. 20 latences (s) : médiane 1.4, p95 3.4, max 6.0
OK — palier 11 terminé.
```

## Pour aller plus loin

1. **Le coût d'une session sans fenêtre.** À l'étape k d'une session, l'agent renvoie S₀ + (k − 1) Δ tokens d'entrée. Avec K = 15 étapes, S₀ = 2 000 et Δ = 500, appelle `cout_tache` sur le total d'entrée. Réponse attendue : 15 × 2 000 + 500 × 15 × 14 / 2 = 82 500 tokens, soit 0,2475 USD d'entrée par session (étape 72, point 7).
2. **Le seuil de rentabilité du cache avec d'autres facteurs.** Un cache d'une heure s'écrit plus cher, par exemple w = 2 (illustratif). Combien de relectures faut-il pour qu'il soit rentable ? Réponse attendue : k > (2 − 1) / (1 − 0,1) = 1,11, donc à partir de deux relectures.
3. **Relier le seau aux relances.** Écrire une fonction qui lève `ErreurTransitoire("429 : débit dépassé")` quand `seau.consommer(3_000)` rend `False`, et la passer à `executer_avec_relances` avec la même `Horloge` que le seau, une base de 20 s, un plafond de 60 s et sans gigue (`gigue=0`). Réponse attendue : avec un seau de 10 000 jetons à 50 par seconde déjà vidé à 1 000 jetons, la première relance attend 20 s, le seau remonte à 2 000, la deuxième attend 40 s, le seau atteint 4 000, et la troisième tentative passe ; la relance laisse au seau le temps de se remplir.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/` ; ouvre le fichier de l'étape qui te bloque, et arrête-toi dès que l'idée qui te manquait est claire.

- [Étape 1 — Les prix et le coût d'une tâche](<solutions/progression/01-Prix-et-cout-d-une-tache.md>) : les constantes illustratives, la formule à quatre termes, et l'erreur qui consiste à oublier les facteurs du cache.
- [Étape 2 — Le seau à jetons](<solutions/progression/02-Seau-a-jetons.md>) : l'état minimal (jetons et dernier instant), la recharge plafonnée, et le refus qui ne retire rien.
- [Étape 3 — L'attente exponentielle et la gigue](<solutions/progression/03-Attente-exponentielle-et-gigue.md>) : le doublement plafonné, la gigue qui raccourcit, le générateur local.
- [Étape 4 — Les relances sur erreur transitoire](<solutions/progression/04-Relances-sur-erreur-transitoire.md>) : n'attraper que ce qui mérite une relance, ne pas attendre après le dernier échec.
- [Étape 5 — Les percentiles et le p95](<solutions/progression/05-Percentiles-et-p95.md>) : le rang le plus proche, le décalage d'indice, et le piège du flottant.
- [Étape 6 — Le budget et les tâches possibles](<solutions/progression/06-Budget-et-taches-possibles.md>) : un dépassement visible, et la partie entière inférieure plutôt que l'arrondi.
- [Étape 7 — Assembler, lancer et retenir](<solutions/progression/07-Assembler-et-lancer.md>) : tous les tests, la démo commentée ligne par ligne, et ce que tu sais maintenant faire.

La solution entière est dans `solutions/agent/production.py`, avec les tests dans `solutions/tests/` et la démo dans `solutions/demo.py`.
