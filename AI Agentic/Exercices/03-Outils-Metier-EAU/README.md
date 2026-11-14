# Palier 03 — Outils métier EAU

> Palier 03 sur 12 · Précédent : [Palier 02 — Schémas et validation](<../02-Schemas-et-Validation/README.md>) · Suivant : [Palier 04 — Registre d'outils](<../04-Registre-d-Outils/README.md>) · Leçons à relire : [Étape 9 — Schémas, exemples EAU](<../../03-Schemas-Outils-et-Premiere-Evaluation/09-Schemas-Exemples-Cas-Usage.md>) · [Étape 10 — Schémas par domaine](<../../03-Schemas-Outils-et-Premiere-Evaluation/10-Schemas-Applications-Domaines.md>) · [Étape 12 — Outils](<../../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>) · [Étape 13 — Six agents EAU](<../../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>) · [Étape 77 — Projet final](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Mode d'emploi : [les douze paliers](<../README.md>)

Un modèle de langage prédit des tokens : il ne calcule pas. Demande-lui la mensualité d'un prêt de 1 000 000 AED à 4,5 % sur 25 ans, il écrira un nombre plausible, à quelques dirhams près, ou à quelques centaines. Une banque ne peut pas vivre avec « à peu près ». La règle de l'agent, écrite dans `REGLES` au palier 01, est donc : « Ne calcule jamais de tête : appelle les outils ». Ce palier écrit les calculs que ces outils exécuteront, au centime près, avec les règles réelles des Émirats.

## Où en est l'agent

Deux paliers sont faits. Le palier 01 (`agent/modele.py`) a posé le port du modèle, avec `FakeLLM`, les blocs `Bloc` et `Reponse`, et le prompt qui sépare les règles des documents non fiables. Le palier 02 (`agent/schemas.py`) a écrit le validateur `validate`, le constructeur `objet` et la préparation du schéma pour le mode strict de l'API. L'agent sait donc parler à un modèle et vérifier la forme d'un JSON. Il ne sait encore rien faire.

```text
                    ┌─────────────────────────────── agent ───────────────────────────────┐
  question ───────► │ construire_prompt (01) ──► boucle (05) ──► porte de l'outil (04)    │
                    │                               ▲                   │   validate (02) │
                    │                               │                   ▼                 │
                    │                  tool_result (observer) ╔════════════════════════╗  │
                    │                                         ║ metier.py (03)   ◄ ICI ║  │
                    │                                         ║ mensualité, ratio,     ║  │
                    │                                         ║ fin de service, TVA,   ║  │
                    │                                         ║ change, IBAN, EID      ║  │
                    │                                         ╚════════════════════════╝  │
                    └─────────────────────────────────────────────────────────────────────┘
```

Dans la boucle percevoir → décider → agir → observer, ce module est le cœur de l'étape « agir ». Le modèle décide **quel** calcul faire et avec quels arguments ; le code de `metier.py` le fait. Ce sont des fonctions pures, sans état, sans réseau, sans modèle : la couche domaine de l'architecture hexagonale. Elles ne savent pas qu'un agent existe. Au palier 04, le registre les enveloppera en outils, chacun avec son schéma. Au palier 09, les garde-fous réutiliseront `iban_ae_valide` et `emirates_id_format_valide` pour masquer les données personnelles du journal. Au palier 12, l'assemblage affichera ses montants avec `fr`.

## Ce que tu vas coder

- Les constantes `ESPACE_FINE`, `AED_PAR_USD`, `TAUX_TVA`, `PLAFOND_CBUAE` et `PLAFOND_RETRAITE` sont fournies dans le squelette : ce sont les chiffres réglementaires, écrits une seule fois.
- `fr(x, decimales)` : affiche un montant à la française, « 5 558,32 ».
- `mensualite(principal, taux_annuel, n_mois)` : la mensualité d'un prêt amortissable.
- `ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)` : le taux d'endettement total de la CBUAE et son verdict.
- `gratuite_fin_de_service(salaire_base_mensuel, annees)` : l'indemnité de fin de service du décret-loi fédéral 33/2021.
- `tva(montant_ht, taux)` : la TVA de 5 %.
- `aed_vers_usd(montant_aed)` et `usd_vers_aed(montant_usd)` : la conversion à la parité fixe de 3,6725 AED pour 1 USD.
- `iban_ae_valide(iban)` : la forme d'un IBAN émirien et sa clé mod 97.
- `emirates_id_format_valide(eid)` : le format d'un numéro d'Emirates ID.

## Rappel de cours

### La mensualité d'un prêt amortissable

On emprunte P au taux annuel t, remboursé en n mensualités égales M. Le taux mensuel vaut :

$$
r = \frac{t}{12}
$$

Le prêt est remboursé quand la valeur actuelle des n mensualités égale le capital. Un dirham payé au mois k vaut aujourd'hui 1/(1 + r)ᵏ dirham, donc :

$$
P = \sum_{k=1}^{n} \frac{M}{(1+r)^{k}}
$$

C'est une série géométrique de raison q = 1/(1 + r). Sa somme vaut q(1 − qⁿ)/(1 − q), et comme q/(1 − q) = 1/r, on en tire la formule à coder :

$$
M = \frac{P\,r}{1-(1+r)^{-n}}
$$

Quand r = 0, le numérateur et le dénominateur valent tous deux 0 : en Python, la division lève `ZeroDivisionError`. La limite existe pourtant, parce que (1 + r)⁻ⁿ = 1 − nr + o(r), et le dénominateur vaut nr + o(r). Elle donne le remboursement sans intérêt :

$$
M = \frac{P}{n} \qquad \text{si} \qquad r = 0
$$

La démonstration complète est à l'[étape 9, point 1](<../../03-Schemas-Outils-et-Premiere-Evaluation/09-Schemas-Exemples-Cas-Usage.md>).

### Le taux d'endettement total

La CBUAE plafonne la part du revenu mensuel R consacrée à **toutes** les mensualités : les D AED déjà remboursés chaque mois et la nouvelle mensualité M.

$$
E = \frac{D + M}{R}
$$

Le dossier est recevable si E ne dépasse pas le plafond : 50 % du revenu, 30 % pour un retraité.

$$
E \le 0{,}50
$$

Regarder M seul est l'erreur classique. Avec D = 15 000, M = 5 558,32 et R = 40 000, M/R vaut 13,9 % et semble anodin, alors que E vaut 51,4 % et dépasse le plafond (étape 9, point 2).

### L'indemnité de fin de service

Pour un salaire de base mensuel S et a années de service (a réel, au prorata), le salaire journalier vaut S/30. Le décret-loi fédéral 33/2021 accorde 21 jours par an pendant les 5 premières années, 30 jours par an au-delà :

$$
j = \frac{S}{30}
$$

$$
G_{brut} = 21\,j\,\min(a, 5) + 30\,j\,\max(a - 5,\ 0)
$$

`min(a, 5)` compte les années de la première tranche, et `max(a - 5, 0)` celles de la seconde, nulles tant que a ≤ 5. L'indemnité est nulle avant un an de service et plafonnée à 24 mois de salaire de base :

$$
G = \begin{cases} 0 & \text{si } a < 1 \\ \min\left(G_{brut},\ 24\,S\right) & \text{si } a \ge 1 \end{cases}
$$

Exprimée en mois de salaire, l'indemnité brute vaut 21 × 5 / 30 = 3,5 mois pour les 5 premières années, puis un mois par année : pour a ≥ 5, elle vaut 3,5 + (a − 5) = a − 1,5 mois. Le plafond de 24 mois mord donc à partir de a = 25,5 ans.

### La TVA et le change

Pour un montant hors taxe H et le taux τ = 5 % :

$$
T = \tau\,H
$$

$$
\text{TTC} = H + T = (1 + \tau)\,H
$$

Le dirham est arrimé au dollar à une parité fixe. Pour un montant A en AED et un montant U en USD :

$$
U = \frac{A}{3{,}6725}
$$

$$
A = 3{,}6725\,U
$$

### La clé de contrôle d'un IBAN

On place les 4 premiers caractères de l'IBAN à la fin, on remplace chaque lettre par un nombre (A = 10, B = 11, …, E = 14, …, Z = 35), et l'on lit le tout comme un entier N. L'IBAN est valide si :

$$
N \equiv 1 \pmod{97}
$$

N a 25 chiffres pour un IBAN émirien : il tient dans un `int` Python, qui n'a pas de taille maximale. À la main, ou dans un langage aux entiers bornés comme Java avec `long`, on lit N chiffre par chiffre en ne gardant que le reste (méthode de Horner) :

$$
\rho_0 = 0 \qquad \rho_k = \left(10\,\rho_{k-1} + d_k\right) \bmod 97
$$

C'est juste parce que le reste d'une somme ou d'un produit ne dépend que des restes des termes : si a = 97q + ρ, alors 10a + d = 97 × 10q + 10ρ + d, qui a le même reste que 10ρ + d. Le dernier ρ est donc N mod 97. Comme 97 est premier et ne divise ni un écart de 1 à 9 ni une puissance de 10, toute erreur sur un seul chiffre change le reste : elle est toujours détectée (étape 9, point 4).

### Les symboles, un par un

$$
P
$$

Le principal, le capital emprunté, en AED, strictement positif ; `principal`.

$$
t
$$

Le taux annuel, en fraction (0,045 pour 4,5 %), positif ou nul ; `taux_annuel`.

$$
r
$$

Le taux mensuel, t/12 : 0,00375 pour 4,5 % par an.

$$
n
$$

Le nombre de mensualités, un entier strictement positif ; `n_mois` (300 pour 25 ans).

$$
M
$$

La mensualité, en AED : ce que rend `mensualite`, et le deuxième argument de `ratio_endettement`.

$$
D
$$

La somme des mensualités déjà en cours, en AED par mois, positive ou nulle ; `mensualites_existantes`.

$$
R
$$

Le revenu mensuel, en AED, strictement positif ; `revenu_mensuel`.

$$
E
$$

Le taux d'endettement total, une fraction (0,288958 pour 28,9 %) ; le premier élément du couple rendu par `ratio_endettement`.

$$
S
$$

Le salaire de base mensuel, en AED, hors indemnités de logement et de transport ; `salaire_base_mensuel`.

$$
a
$$

L'ancienneté, en années, réelle et positive ou nulle (3,5 pour trois ans et demi) ; `annees`.

$$
j
$$

Le salaire journalier, S/30 : 333,33 AED pour 10 000 AED de base.

$$
G
$$

L'indemnité de fin de service, en AED ; ce que rend `gratuite_fin_de_service`.

$$
H
$$

Le montant hors taxe, en AED ; `montant_ht`.

$$
\tau
$$

Le taux de TVA, 0,05 aux Émirats ; `taux`, qui vaut `TAUX_TVA` par défaut.

$$
T
$$

Le montant de la TVA, en AED ; ce que rend `tva`.

$$
A
$$

Un montant en AED ; `montant_aed`.

$$
U
$$

Un montant en USD ; `montant_usd`.

$$
N
$$

L'entier obtenu à partir de l'IBAN réarrangé, lettres converties : 25 chiffres pour un IBAN émirien.

$$
d_k
$$

Le k-ième chiffre de N, lu de gauche à droite.

$$
\rho_k
$$

Le reste modulo 97 des k premiers chiffres de N ; le dernier vaut N mod 97.

## Spécification

Toutes les fonctions refusent une entrée hors de leur domaine par `ValueError`, avec un message clair, sauf les deux contrôles d'identifiants, qui répondent par `False` : un identifiant mal formé est une réponse normale, pas une erreur du programme. Aucune fonction n'arrondit : l'arrondi au centime se fait à l'affichage (`fr`) ou dans l'outil (palier 04).

### Les constantes

```python
# [extrait] spécification
ESPACE_FINE = chr(0x202F)      # espace fine insécable (U+202F), séparateur de milliers français
AED_PAR_USD = 3.6725           # parité fixe du dirham
TAUX_TVA = 0.05
PLAFOND_CBUAE = 0.50
PLAFOND_RETRAITE = 0.30
```

Ces cinq valeurs sont fournies. Chacune est écrite une fois et réutilisée partout : si la règle change, on change une ligne. `ESPACE_FINE` s'écrit avec `chr(0x202F)` plutôt qu'en collant le caractère dans le source, où il serait invisible et confondu avec une espace ordinaire. Le test `TestTvaEtChange.test_conversion` vérifie `AED_PAR_USD == 3.6725`.

### fr

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`fr(x, decimales)`** — Cette fonction doit être le calligraphe de la banque, celui qui recopie chaque montant à la française avant qu'il n'arrive sous les yeux du client : elle reçoit un nombre et un nombre de décimales, 2 par défaut, et renvoie une chaîne où les milliers sont séparés par l'espace fine insécable `ESPACE_FINE` et où la virgule marque les décimales. Elle ne lève rien et n'arrondit qu'à l'affichage : 5558,32 doit devenir « 5 558,32 », un million sans décimale « 1 000 000 », et 28,9 avec une décimale « 28,9 ». C'est elle que l'assemblage du palier 12 utilisera pour afficher tous ses montants.

```python
# [extrait] spécification
def fr(x: float, decimales: int = 2) -> str: ...
```

Rend le montant avec `decimales` décimales, l'espace fine comme séparateur de milliers et la virgule décimale. La fonction ne lève rien.

**Exemple à la main.** Le format anglais `f"{5558.32:,.2f}"` donne « 5,558.32 » : une virgule pour les milliers, un point pour les décimales. On remplace d'abord la virgule par l'espace fine (« 5 558.32 »), puis le point par une virgule (« 5 558,32 »). Dans l'autre ordre, le point deviendrait une virgule, puis toutes les virgules deviendraient des espaces, et l'on obtiendrait « 5 558 32 ». De même, `fr(1_000_000, 0)` donne « 1,000,000 », puis « 1 000 000 », et `fr(28.9, 1)` donne « 28.9 », puis « 28,9 ». Test : `TestFormatage.test_montants_a_la_francaise`.

### mensualite

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`mensualite(principal, taux_annuel, n_mois)`** — Cette fonction doit faire le travail du conseiller de crédit qui, devant un client venu acheter son appartement, calcule ce qu'il paiera chaque mois : elle reçoit le capital emprunté en AED, le taux annuel en fraction et le nombre de mensualités, et renvoie la mensualité M d'un prêt amortissable, non arrondie. Elle lève `ValueError` si le capital ou la durée sont nuls ou négatifs, ou si le taux est négatif ; un taux nul reste permis et doit rendre le simple partage P/n, soit 5 000 AED pour 120 000 AED sur 24 mois. Pour 1 000 000 AED à 4,5 % sur 300 mois, elle doit donner environ 5 558,32 AED, la mensualité que l'outil du palier 04 exposera au modèle.

```python
# [extrait] spécification
def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float: ...
```

Rend M, non arrondie. Lève `ValueError` si `principal <= 0`, `n_mois <= 0` ou `taux_annuel < 0`. Un taux nul est permis et rend P/n.

**Exemple à la main.** P = 1 000 000 AED, t = 0,045, n = 300 mois.

1. r = 0,045 / 12 = 0,00375.
2. ln(1,00375) ≈ 0,00375 − 0,00375²/2 = 0,0037430, donc 300 × ln(1,00375) = 1,12290, et (1,00375)³⁰⁰ = exp(1,12290) = 3,073743.
3. (1,00375)⁻³⁰⁰ = 1 / 3,073743 = 0,325336, et le dénominateur vaut 1 − 0,325336 = 0,674664.
4. Le numérateur vaut P r = 1 000 000 × 0,00375 = 3 750.
5. M = 3 750 / 0,674664 = 5 558,3248, soit 5 558,32 AED au centime.

Avec un taux nul, `mensualite(120_000, 0.0, 24)` vaut 120 000 / 24 = 5 000 AED exactement. Les trois appels `mensualite(0, 0.045, 300)`, `mensualite(1_000, 0.045, 0)` et `mensualite(1_000, -0.01, 12)` lèvent `ValueError`. Tests : `TestCredit.test_mensualite_hypotheque`, `test_mensualite_taux_nul`, `test_mensualite_entrees_invalides`.

### ratio_endettement

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — Cette fonction doit être l'analyste des risques qui pose sur la même balance toutes les mensualités d'un client, et non la seule nouvelle : elle reçoit les mensualités déjà en cours, la nouvelle mensualité, le revenu mensuel et le plafond, `PLAFOND_CBUAE` soit 0,50 par défaut, et renvoie le couple formé du taux d'endettement total E = (D + M) / R et du booléen qui dit si E ne dépasse pas le plafond, l'égalité étant recevable. Elle lève `ValueError` sur un revenu nul ou négatif, une mensualité négative ou un plafond hors de ]0, 1]. Le client C-1, avec 6 000 AED de crédits en cours, 5 558,32 AED de nouvelle mensualité et 40 000 AED de revenu, doit obtenir 0,288958 et un dossier recevable, tandis que le retraité C-2, au plafond de 0,30, doit être refusé à 0,313958.

```python
# [extrait] spécification
def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = PLAFOND_CBUAE) -> tuple[float, bool]: ...
```

Rend le couple (E, E ≤ plafond). Un ratio exactement égal au plafond est recevable. Lève `ValueError` si le revenu est ≤ 0, si l'une des deux mensualités est négative, ou si le plafond sort de ]0, 1].

**Exemple à la main.** Client C-1 : D = 6 000 AED, M = 5 558,32 AED, R = 40 000 AED. E = (6 000 + 5 558,32) / 40 000 = 11 558,32 / 40 000 = 0,288958, sous 0,50 : le couple vaut (0,288958 ; vrai). Client retraité C-2, avec `plafond=0.30` : (7 000 + 5 558,32) / 40 000 = 12 558,32 / 40 000 = 0,313958, au-dessus de 0,30 : (0,313958 ; faux). À la limite, (10 000 + 10 000) / 40 000 = 0,50 exactement : recevable. Les appels avec un revenu nul, des mensualités existantes de −1 ou un plafond de 1,5 lèvent `ValueError`. Tests : `TestCredit.test_ratio_toutes_les_mensualites`, `test_ratio_plafond_retraite`, `test_ratio_entrees_invalides`.

### gratuite_fin_de_service

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`gratuite_fin_de_service(salaire_base_mensuel, annees)`** — Cette fonction doit tenir le rôle du gestionnaire de paie qui prépare le solde de tout compte d'un salarié qui s'en va : elle reçoit le salaire de base mensuel en AED et l'ancienneté en années, éventuellement fractionnaire, et renvoie l'indemnité de fin de service du décret-loi fédéral 33/2021, non arrondie, soit 21 jours de salaire par an pour les cinq premières années et 30 jours au-delà, le jour valant le salaire divisé par 30. Moins d'un an de service rend `0.0`, l'indemnité est plafonnée à 24 mois de salaire, et un salaire nul ou négatif, comme une ancienneté négative, lève `ValueError`. Le salarié C-3, à 10 000 AED de base et sept ans de service, doit recevoir 55 000 AED, et quarante ans de service doivent être ramenés au plafond de 240 000 AED.

```python
# [extrait] spécification
def gratuite_fin_de_service(salaire_base_mensuel: float, annees: float) -> float: ...
```

Rend G en AED, non arrondie. Moins d'un an de service rend `0.0`. Lève `ValueError` si le salaire est ≤ 0 ou si les années sont négatives.

**Exemple à la main.** Salarié C-3, S = 10 000 AED, a = 7 ans. Le salaire journalier vaut 10 000 / 30 = 333,33 AED. Première tranche : min(7, 5) = 5 ans × 21 jours = 105 jours, soit 105 × 333,33 = 35 000 AED. Seconde tranche : max(7 − 5, 0) = 2 ans × 30 jours = 60 jours, soit 20 000 AED. Total : 55 000 AED, sous le plafond de 24 × 10 000 = 240 000 AED. Avec 5 ans, seule la première tranche compte : 35 000 AED. Avec 0,9 an : 0. Avec 40 ans : 105 + 35 × 30 = 1 155 jours, soit 385 000 AED, ramenés au plafond de 240 000 AED. Tests : `TestFinDeService.test_sept_ans`, `test_moins_d_un_an_et_plafond`, `test_entrees_invalides`.

### tva

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`tva(montant_ht, taux)`** — Cette fonction doit faire le geste du caissier qui sépare, sur le ticket, la part de l'État de celle du vendeur : elle reçoit un montant hors taxe en AED et un taux, `TAUX_TVA` soit 0,05 par défaut, et renvoie le montant de la TVA seule, pas le prix toutes taxes comprises. Elle lève `ValueError` si le montant est négatif ou si le taux sort de [0, 1], mais accepte un taux nul, celui d'une première livraison d'un bien résidentiel. Sur 12 000 AED hors taxe, elle doit rendre 600 AED, ce qui porte le TTC à 12 600 AED.

```python
# [extrait] spécification
def tva(montant_ht: float, taux: float = TAUX_TVA) -> float: ...
```

Rend la TVA seule, pas le TTC. Lève `ValueError` si le montant est négatif ou si le taux sort de [0, 1]. Un taux nul est permis : c'est le cas d'une première livraison d'un bien résidentiel.

**Exemple à la main.** `tva(12_000)` = 12 000 × 0,05 = 600 AED, soit un TTC de 12 600 AED. `tva(12_000, taux=0.0)` vaut 0. `tva(-1)` lève `ValueError`. Test : `TestTvaEtChange.test_tva`.

### aed_vers_usd et usd_vers_aed

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`aed_vers_usd(montant_aed)`** — Cette fonction doit être le changeur du souk qui, avec un taux affiché une fois pour toutes, convertit des dirhams en dollars : elle reçoit un montant en AED, lève `ValueError` s'il est négatif, et renvoie ce montant divisé par la parité fixe `AED_PAR_USD`, 3,6725, sans arrondi. La mensualité de 5 558,32 AED doit ainsi valoir environ 1 513,4976 USD, et c'est cette conversion que l'outil de change du palier 04 proposera au modèle.

**`usd_vers_aed(montant_usd)`** — Celle-ci est le même changeur pris dans l'autre sens du comptoir : elle reçoit un montant en USD, lève `ValueError` s'il est négatif, et renvoie ce montant multiplié par 3,6725, toujours sans arrondi, de sorte que 0,0384 USD devient 0,141024 AED. Associée à `aed_vers_usd`, elle doit permettre un aller-retour fidèle : 180 000 AED convertis en dollars puis ramenés en dirhams doivent redonner 180 000 AED, à 10⁻⁶ près en flottants.

```python
# [extrait] spécification
def aed_vers_usd(montant_aed: float) -> float: ...
def usd_vers_aed(montant_usd: float) -> float: ...
```

Divisent ou multiplient par `AED_PAR_USD`, sans arrondi. Un montant négatif lève `ValueError`.

**Exemple à la main.** 5 558,32 AED en USD : 3,6725 × 1 500 = 5 508,75 ; il reste 5 558,32 − 5 508,75 = 49,57 AED, et 49,57 / 3,6725 = 13,4976 ; donc 1 513,4976 USD. Dans l'autre sens, 0,0384 USD × 3,6725 = 0,141024 AED. L'aller-retour `usd_vers_aed(aed_vers_usd(180_000))` redonne 180 000 AED (à 10⁻⁶ près, en flottants). `aed_vers_usd(-5)` lève `ValueError`. Test : `TestTvaEtChange.test_conversion`.

### iban_ae_valide

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`iban_ae_valide(iban)`** — Cette fonction doit être le guichetier méfiant qui, avant tout virement, vérifie que le numéro de compte tendu par le client a la bonne forme et la bonne clé : elle reçoit une chaîne, la normalise en retirant les espaces et en passant aux majuscules, puis renvoie `False` si elle n'a pas 23 caractères, ne commence pas par « AE » ou contient autre chose que des chiffres après ces deux lettres. Si la forme est bonne, elle renvoie le résultat du test de la clé, N mod 97 = 1, sans jamais lever d'exception, car un IBAN mal formé est une réponse normale. L'IBAN « AE07 0331 2345 6789 0123 456 » doit être accepté, tout comme sa version en minuscules sans espaces, la même suite avec la clé 08 refusée, et les gardes-fous du palier 09 réutiliseront cette fonction pour masquer les IBAN dans le journal.

```python
# [extrait] spécification
def iban_ae_valide(iban: str) -> bool: ...
```

Normalise (espaces retirés, majuscules), puis rend `False` si la chaîne n'a pas 23 caractères, ne commence pas par « AE » ou contient autre chose que des chiffres après « AE ». Sinon, rend le résultat du test N mod 97 = 1. Une forme fausse n'est pas une erreur du programme : la fonction rend `False`, sans exception (voir tout de même le défi 3 de « Pour aller plus loin »).

**Exemple à la main.** IBAN « AE07 0331 2345 6789 0123 456 ». Sans espaces : « AE070331234567890123456 », 23 caractères, « AE » suivi de 21 chiffres. On déplace « AE07 » à la fin : « 0331234567890123456AE07 ». On remplace A par 10 et E par 14 : N s'écrit « 0331234567890123456101407 », 25 chiffres. On lit ces chiffres un par un, en ne gardant que le reste modulo 97 :

| k | dₖ | 10 × ρ + dₖ | ρₖ |
| --- | --- | --- | --- |
| 1 | 0 | 0 | 0 |
| 2 | 3 | 3 | 3 |
| 3 | 3 | 33 | 33 |
| 4 | 1 | 331 | 331 − 3 × 97 = 40 |
| 5 | 2 | 402 | 402 − 4 × 97 = 14 |
| 6 | 3 | 143 | 143 − 97 = 46 |
| 7 | 4 | 464 | 464 − 4 × 97 = 76 |
| 8 | 5 | 765 | 765 − 7 × 97 = 86 |
| 9 | 6 | 866 | 866 − 8 × 97 = 90 |
| 10 | 7 | 907 | 907 − 9 × 97 = 34 |
| 11 | 8 | 348 | 348 − 3 × 97 = 57 |
| 12 | 9 | 579 | 579 − 5 × 97 = 94 |
| 13 | 0 | 940 | 940 − 9 × 97 = 67 |
| 14 | 1 | 671 | 671 − 6 × 97 = 89 |
| 15 | 2 | 892 | 892 − 9 × 97 = 19 |
| 16 | 3 | 193 | 193 − 97 = 96 |
| 17 | 4 | 964 | 964 − 9 × 97 = 91 |
| 18 | 5 | 915 | 915 − 9 × 97 = 42 |
| 19 | 6 | 426 | 426 − 4 × 97 = 38 |
| 20 | 1 (de A = 10) | 381 | 381 − 3 × 97 = 90 |
| 21 | 0 (de A = 10) | 900 | 900 − 9 × 97 = 27 |
| 22 | 1 (de E = 14) | 271 | 271 − 2 × 97 = 77 |
| 23 | 4 (de E = 14) | 774 | 774 − 7 × 97 = 95 |
| 24 | 0 (clé) | 950 | 950 − 9 × 97 = 77 |
| 25 | 7 (clé) | 777 | 777 − 8 × 97 = 1 |

Le reste final vaut 1 : l'IBAN est valide. Avec la clé 08, seule la dernière ligne change : 10 × 77 + 8 = 778, et 778 − 776 = 2 ≠ 1, l'IBAN est refusé. La version en minuscules et sans espaces, « ae070331234567890123456 », est acceptée après normalisation ; « AE07 0331 2345 6789 0123 45 » (22 caractères) et « FR07 0331 2345 6789 0123 456 » sont refusés sur la forme, avant tout calcul. Test : `TestIdentifiants.test_iban`.

### emirates_id_format_valide

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`emirates_id_format_valide(eid)`** — Cette fonction doit faire le contrôle rapide d'un agent d'accueil qui jette un œil à la carte d'identité sans interroger le registre national : elle reçoit une chaîne, en retire les tirets et les espaces, et renvoie vrai si et seulement s'il reste exactement 15 caractères, tous des chiffres, commençant par 784, l'indicatif numérique des Émirats. Elle ne vérifie pas le chiffre de contrôle final et ne lève jamais d'exception : « 784-1990-1234567-1 » et sa forme compacte doivent passer, « 785-1990-1234567-1 » et « 784-1990-123456-1 », qui n'a que 14 chiffres, doivent être refusés.

```python
# [extrait] spécification
def emirates_id_format_valide(eid: str) -> bool: ...
```

Retire les tirets et les espaces, puis rend vrai si et seulement s'il reste exactement 15 caractères, tous des chiffres, commençant par « 784 », l'indicatif ISO 3166 numérique des Émirats. La fonction ne contrôle pas le dernier chiffre (clé) et ne lève jamais d'exception.

**Exemple à la main.** « 784-1990-1234567-1 » devient « 784199012345671 » : 3 + 4 + 7 + 1 = 15 chiffres, préfixe 784, donc valide ; la forme compacte « 784199012345671 » aussi. « 785-1990-1234567-1 » a 15 chiffres mais commence par 785 : refusé. « 784-1990-123456-1 » n'a que 3 + 4 + 6 + 1 = 14 chiffres : refusé. Test : `TestIdentifiants.test_emirates_id`.

## Squelette algorithmique

```text
ALGORITHME Mensualité
ENTRÉES : principal P > 0, taux annuel t ≥ 0, nombre de mois n > 0
SORTIE  : la mensualité M
  SI P ≤ 0 OU n ≤ 0 OU t < 0 ALORS LEVER ErreurDeValeur
  r ← t / 12
  SI r = 0 ALORS RENDRE P / n
  RENDRE P × r / (1 − (1 + r)^(−n))

ALGORITHME RatioEndettement
ENTRÉES : mensualités existantes D ≥ 0, nouvelle mensualité M ≥ 0, revenu R > 0, plafond p dans ]0, 1]
SORTIE  : (E, recevable)
  vérifier R > 0, D ≥ 0, M ≥ 0, 0 < p ≤ 1, sinon LEVER ErreurDeValeur
  E ← (D + M) / R
  RENDRE (E, E ≤ p)

ALGORITHME FinDeService
ENTRÉES : salaire de base S > 0, ancienneté a ≥ 0
SORTIE  : indemnité G
  vérifier S > 0 et a ≥ 0, sinon LEVER ErreurDeValeur
  SI a < 1 ALORS RENDRE 0
  j ← S / 30
  brut ← min(a, 5) × 21 × j + max(a − 5, 0) × 30 × j
  RENDRE min(brut, 24 × S)

ALGORITHME CléIBAN
ENTRÉE  : chaîne iban
SORTIE  : vrai ou faux
  s ← iban sans espaces, en majuscules
  SI longueur(s) ≠ 23 OU s ne commence pas par « AE » OU s privée de « AE » n'est pas faite de chiffres
     ALORS RENDRE faux
  s ← (s privée de ses 4 premiers caractères) suivie de (ses 4 premiers caractères)
  texte ← ""
  POUR CHAQUE caractère c DE s :
     texte ← texte suivi de l'écriture décimale de valeur(c)      (chiffre : lui-même ; A → 10 … Z → 35)
  RENDRE (entier(texte) mod 97 = 1)

ALGORITHME FormatEmiratesID
ENTRÉE  : chaîne eid
SORTIE  : vrai ou faux
  c ← eid sans tirets ni espaces
  RENDRE longueur(c) = 15 ET c n'a que des chiffres ET c commence par « 784 »
```

**Complexité.** Chaque fonction de calcul fait un nombre fixe d'opérations : O(1) en temps et en mémoire, la puissance (1 + r)⁻ⁿ comprise, que la bibliothèque mathématique calcule en temps constant sur des flottants. Les deux contrôles d'identifiants parcourent la chaîne une ou deux fois : O(L) pour une chaîne de L caractères, avec L = 23 pour un IBAN et 15 pour un Emirates ID, donc un temps négligeable. Le grand entier de 25 chiffres reste petit pour Python.

**Du squelette au code.** Mensualité devient `mensualite`, avec `taux_annuel / 12` et l'opérateur `**` pour la puissance. RatioEndettement devient `ratio_endettement`, dont le plafond par défaut est `PLAFOND_CBUAE`. FinDeService devient `gratuite_fin_de_service`, où `min` et `max` remplacent les deux tranches. Pour la TVA et le change, `tva`, `aed_vers_usd` et `usd_vers_aed` s'écrivent en une ligne après leur garde. CléIBAN devient `iban_ae_valide` : la valeur d'un caractère s'obtient par `int(c, 36)`, qui lit un caractère en base 36 (les chiffres 0 à 9, puis A = 10 jusqu'à Z = 35). FormatEmiratesID devient `emirates_id_format_valide`. L'affichage `fr` n'a pas d'algorithme : deux remplacements, dans le bon ordre.

## Cas d'usage aux Émirats

Les montants, salaires et durées ci-dessous sont illustratifs ; les règles (plafond CBUAE, fin de service, TVA, parité, IBAN, Emirates ID) sont les règles réelles, à confirmer avec le texte en vigueur avant tout usage réel.

### Banque — pré-instruire une hypothèque sans calcul de tête

La banque B-1 reçoit, par son assistant en ligne, la demande du client C-1 : 1 000 000 AED sur 25 ans à 4,5 %. Le modèle appelle `mensualite` (5 558,32 AED), puis `ratio_endettement` avec les 6 000 AED de crédit auto en cours et 40 000 AED de revenu : 28,9 %, recevable. Il donne aussi l'équivalent en dollars, `aed_vers_usd`, soit 1 513,50 USD, parce que le client est payé en USD. Le conseiller voit en plus la marge de manœuvre du client : la dette existante maximale compatible avec ce prêt est 0,5 × 40 000 − 5 558,32 = 14 441,68 AED par mois. Le même jour, C-2, retraité, demande le même prêt avec 7 000 AED de crédits en cours : 31,4 %, au-dessus du plafond de 30 % des retraités, et `ratio_endettement(..., plafond=PLAFOND_RETRAITE)` rend un refus que l'assistant explique au lieu de le négocier.

### RH — un solde de tout compte juste au dirham

Un cabinet RH prépare les soldes de tout compte de plusieurs entreprises clientes. Pour le salarié C-3, 10 000 AED de salaire de base et 7 ans de service, `gratuite_fin_de_service` rend 55 000 AED. Pour C-4, 8 000 AED de base et 22 ans, le salaire journalier vaut 266,67 AED et l'indemnité 105 + 17 × 30 = 615 jours, soit 164 000 AED, sous le plafond de 24 × 8 000 = 192 000 AED : le plafond ne mordrait qu'à partir de 25,5 ans de service. L'erreur classique serait de calculer sur le salaire total (base plus logement plus transport) : le décret-loi ne retient que la base, et c'est pourquoi le paramètre s'appelle `salaire_base_mensuel`. Les montants sont affichés avec `fr` dans la lettre au salarié.

### BTP — une situation de travaux payée sur le bon compte

L'agence A-3 d'un groupe de construction reçoit d'un sous-traitant une situation de travaux de 120 000 AED HT. `tva` donne 6 000 AED, soit 126 000 AED TTC, que l'agent compare au TTC de la facture. L'IBAN du sous-traitant, « AE07 0331 2345 6789 0123 456 », passe `iban_ae_valide`. Un courriel qui demande de payer plutôt sur « AE08 0331 2345 6789 0123 456 », qui ne diffère que par la clé, est arrêté avant tout virement : le reste vaut 2, pas 1. Comme le mod 97 détecte toute erreur sur un seul chiffre et toute inversion de deux chiffres voisins, une faute de frappe ne peut pas envoyer l'argent sur un autre compte valide.

## Travail à faire

Toutes les commandes se lancent dans PowerShell, depuis le dossier `projet/` du palier. Si `python` ouvre le Microsoft Store, remplace-le par le chemin complet `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.

1. Ouvre `projet/agent/metier.py`. Les constantes sont fournies ; chaque fonction a sa docstring, des `# TODO` et un `raise NotImplementedError`. Lance une première fois les tests : les 32 tests des paliers 01 et 02 passent, les 14 du palier 03 échouent par `NotImplementedError`.

```text
cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\03-Outils-Metier-EAU\projet"
python -m unittest -v tests.test_03_metier
```

2. Code `fr`, puis lance `python -m unittest -v tests.test_03_metier.TestFormatage`.
3. Code `mensualite` et `ratio_endettement`, puis lance `python -m unittest -v tests.test_03_metier.TestCredit` (6 tests).
4. Code `gratuite_fin_de_service`, puis lance `python -m unittest -v tests.test_03_metier.TestFinDeService` (3 tests).
5. Code `tva`, `aed_vers_usd` et `usd_vers_aed`, puis lance `python -m unittest -v tests.test_03_metier.TestTvaEtChange` (2 tests).
6. Code `iban_ae_valide` et `emirates_id_format_valide`, puis lance `python -m unittest -v tests.test_03_metier.TestIdentifiants` (2 tests).
7. Lance toute la suite, puis la démo :

```text
python -m unittest -v
python demo.py
```

## Critères de réussite

- `python -m unittest -v` affiche `Ran 46 tests` puis `OK` : les 32 tests des paliers 01 et 02 et les 14 tests du palier 03.
- `python demo.py` affiche exactement la sortie ci-dessous. Le dernier chiffre de chaque montant compte : une mensualité de 5 558,33 AED trahit un arrondi fait trop tôt.
- Aucune fonction ne fait d'arrondi, et aucune ne lit l'heure, le réseau ou un fichier.

### Sortie attendue de demo.py

```text
Palier 03 — dossiers des clients C-1 à C-4 (montants en AED, parité 3,6725 AED pour 1 USD)
1. C-1, hypothèque de 1 000 000 AED à 4,5 % sur 300 mois : mensualité 5 558,32 AED = 1 513,50 USD
   endettement (6 000 + 5 558,32) / 40 000 = 28,90 % → recevable : True
2. C-2, retraité, 7 000 AED de crédits en cours : 31,40 % > 30 % → recevable : False
3. C-3, salaire de base 10 000 AED, 7 ans : fin de service 55 000,00 AED
   même salaire, 40 ans : plafonnée à 24 mois, 240 000,00 AED
4. Agence A-3, situation de travaux 120 000 AED HT : TVA 6 000,00 AED, TTC 126 000,00 AED
5. IBAN AE07 0331 2345 6789 0123 456 : clé mod 97 valide = True
5. IBAN AE08 0331 2345 6789 0123 456 : clé mod 97 valide = False
6. Emirates ID 784-1990-1234567-1 : format valide = True
6. Emirates ID 785-1990-1234567-1 : format valide = False
OK — palier 03 terminé.
```

## Pour aller plus loin

1. **La capacité d'emprunt.** Écris `principal_max(mensualite_max, taux_annuel, n_mois)`, l'inverse de `mensualite`, et calcule le prêt maximal de C-1 sur 300 mois à 4,5 %, sachant que ses mensualités totales ne doivent pas dépasser 50 % de 40 000 AED. Réponse attendue : la mensualité disponible vaut 20 000 − 6 000 = 14 000 AED, et P = 14 000 × 0,674664 / 0,00375 ≈ 2 518 744,51 AED.
2. **Calculer la clé d'un IBAN.** Écris `cle_iban_ae(bban)`, qui reçoit les 19 chiffres après la clé et rend les deux chiffres de clé. Réponse attendue : on calcule le reste ρ de l'IBAN réarrangé avec la clé « 00 », puis la clé vaut 98 − ρ ; pour « 0331234567890123456 », ρ = 91 (10 × 77 + 0 = 770, et 770 − 7 × 97 = 91), donc la clé vaut 07.
3. **Des chiffres qui n'en sont pas.** En Python, `"²".isdigit()` vaut `True`, comme `"٣".isdigit()` (le chiffre 3 arabe-indien, courant aux Émirats). Que rend `iban_ae_valide("AE07²331234567890123456")`, et comment rendre la garde de forme étanche ? Réponse attendue : la forme passe, puis `int("²", 36)` lève `ValueError` ; exiger aussi `s.isascii()` dans la garde refuse l'exposant, et du même coup les chiffres arabes-indiens, qu'un IBAN n'emploie pas.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`. Ouvre seulement le fichier de l'étape qui te bloque :

- [01 — Les constantes et l'affichage français](<solutions/progression/01-Constantes-et-affichage-fr.md>) : pourquoi une constante par règle, et l'ordre des deux remplacements de `fr`.
- [02 — La mensualité](<solutions/progression/02-Mensualite.md>) : la formule, la branche du taux nul et les gardes.
- [03 — Le taux d'endettement](<solutions/progression/03-Ratio-d-endettement.md>) : additionner toutes les mensualités, et un plafond en paramètre.
- [04 — La fin de service](<solutions/progression/04-Fin-de-service.md>) : deux tranches avec `min` et `max`, et le plafond de 24 mois.
- [05 — La TVA et le change](<solutions/progression/05-TVA-et-change.md>) : trois fonctions d'une ligne, et pourquoi elles n'arrondissent pas.
- [06 — L'IBAN et l'Emirates ID](<solutions/progression/06-IBAN-et-Emirates-ID.md>) : le mod 97 en Python avec `int(c, 36)`, et un contrôle de format sans regex.
- [07 — Assemblage et démo](<solutions/progression/07-Assemblage-et-demo.md>) : le module entier, tous les tests, la démo et le passage au palier 04.

La solution complète est dans `solutions/agent/metier.py` ; `solutions/demo.py` et `solutions/tests/` sont identiques à ceux de `projet/`.
