# Étape 9 — Schémas — Exemples et cas d'usage

> Étape 9 du parcours · Prérequis : [Définitions des schémas](<08-Schemas-Definitions-Fondamentaux.md>) · Suite : [Les schémas par domaine réglementé](<10-Schemas-Applications-Domaines.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, Product Engineers, Forward-Deployed Engineers

L'étape 8 a construit le validateur. Ce fichier l'applique à six contrats réels des Émirats : une demande de crédit, une estimation immobilière, un ordre de swap, une déclaration de sinistre, une fiche d'embauche et une facture de sous-traitant. Pour chacun, on montre le schéma, une instance valide, plusieurs instances invalides, et la décision que l'agent en tire. L'ancienne version de ce fichier citait quatre domaines en une ligne chacun, sans montrer un seul schéma, et omettait les RH ; elle mentionnait aussi le DPE pour l'immobilier, un diagnostic énergétique français qui n'a pas cours aux Émirats.

## La méthode : le schéma, puis les règles, puis la décision

Chaque contrôle se fait en trois temps, toujours dans cet ordre.

1. **La forme**, par `validate` (étape 8) : types, champs obligatoires, bornes, motifs, énumérations.
2. **Le sens**, par une fonction de règles propre au domaine : les règles inter-champs (une durée qui dépend du type de prêt, deux dates à comparer, un TTC à recalculer) et les contrôles métier qu'un motif ne peut pas faire (la clé mod 97 d'un IBAN, l'existence d'une date dans le calendrier).
3. **La décision** : `ok` (l'agent continue), `schema` (la boucle de réparation de l'étape 8 renvoie les erreurs au modèle) ou `metier` (le dossier est refusé, ou transmis à un humain avec son motif).

L'ordre n'est pas un détail : les règles supposent une instance bien formée, et elles planteraient sur une durée écrite en texte (démonstration, point 5). Le tableau suivant sépare, pour chaque cas, la **fonction de contrôle**, le **seuil** qu'elle applique et la **métrique** que l'on suit en production.

| Cas | Champs critiques du schéma | Fonction de contrôle (règle inter-champs) | Seuil | Métrique suivie |
|---|---|---|---|---|
| Crédit | montant > 0, durée de 12 à 300 mois, revenu > 0 | endettement total = (mensualités existantes + nouvelle) / revenu ; prêt personnel : 48 mois et 20 salaires au plus | 50 % (30 % pour un retraité) | part des dossiers recevables au premier passage |
| Estimation | émirat parmi les 7, surface > 0, prix au sqft > 0, au moins 3 comparables | prix estimé = surface × prix au sqft ; estimation dans sa fourchette | 1 AED | écart relatif entre estimation et prix de vente |
| Swap | adresse `0x` + 40 caractères hexadécimaux, glissement dans [0 ; 0,05] | minimum reçu = quantité × prix × (1 − glissement) ; pool en liste blanche | 0,01 AED | ordres bloqués, par motif |
| Sinistre | dates AAAA-MM-JJ, montants ≥ 0, vétusté dans [0 ; 1] | date existante ; date du sinistre ≤ date de déclaration | 0 jour | déclarations ressaisies à la main |
| Embauche | Emirates ID, nationalité sur 2 lettres, salaires > 0 | code ISO 3166-1 attribué ; base ≤ total ; régime de fin de service cohérent | égalité stricte | rejets de paie WPS |
| Facture | IBAN `AE` + 21 chiffres, montants > 0 | IBAN mod 97 = 1 ; TVA = 5 % du HT ; écart entre TTC et HT × 1,05 | 0,01 AED | factures rejetées, par fournisseur |

## Cas d'usage réels aux Émirats

Les prix, salaires et volumes ci-dessous sont illustratifs ; les règles réglementaires citées (plafonds de la CBUAE, TVA de 5 %, frais de transfert de 4 % de la DLD, régimes de fin de service) sont celles en vigueur à la date de vérification du parcours, à confirmer avec le texte en vigueur avant tout usage réel.

### Banque — une demande de crédit recevable ou non

```json
{
  "type": "object",
  "properties": {
    "type_pret": {"type": "string", "enum": ["hypothecaire", "personnel"]},
    "montant_aed": {"type": "number", "exclusiveMinimum": 0},
    "taux_annuel": {"type": "number", "minimum": 0, "maximum": 0.3},
    "duree_mois": {"type": "integer", "minimum": 12, "maximum": 300},
    "revenu_mensuel_aed": {"type": "number", "exclusiveMinimum": 0},
    "mensualites_existantes_aed": {"type": "number", "minimum": 0},
    "retraite": {"type": "boolean"}
  },
  "required": ["type_pret", "montant_aed", "taux_annuel", "duree_mois", "revenu_mensuel_aed", "mensualites_existantes_aed", "retraite"],
  "additionalProperties": false
}
```

Une banque de détail de Dubaï reçoit des demandes de prêt hypothécaire et personnel que l'agent de l'étape 8 a déjà extraites en JSON ; il s'agit maintenant de dire si chaque dossier est recevable avant de le transmettre à un analyste. Les fonctions s'enchaînent ainsi : `validate` contre ce schéma, puis `regles_credit`, qui appelle `mensualite` puis `ratio_endettement`, deux fonctions du code canonique. Pour une hypothèque de 1 000 000 AED à 4,5 % sur 300 mois, la mensualité vaut 5 558,32 AED ; avec 6 000 AED de mensualités existantes et 40 000 AED de revenu, l'endettement total vaut (6 000 + 5 558,32) / 40 000 = 28,9 %, sous le plafond de 50 % de la CBUAE, et le dossier est recevable. Le même client avec 15 000 AED de mensualités existantes atteint 51,4 % et le dossier est refusé, alors que la nouvelle mensualité seule ne représente que 13,9 % du revenu : une règle qui ne regarderait qu'elle laisserait passer un client surendetté (démonstration, point 2). Pour un prêt personnel, deux plafonds supplémentaires de la CBUAE s'appliquent, 48 mois et 20 fois le salaire mensuel ; pour un retraité, le plafond d'endettement descend à 30 %, si bien qu'une pension de 20 000 AED avec 1 000 AED de dettes existantes donne 32,8 % et un refus. Le garde-fou est l'ordre des contrôles : aucune règle ne s'exécute sur une instance mal formée, et un refus métier n'est jamais « réparé » par le modèle, il est expliqué au client. On suit la part des dossiers recevables au premier passage et la répartition des motifs de refus, qui révèle si les conseillers orientent mal les demandes.

| Instance | Verdict | Motif |
|---|---|---|
| Hypothèque de 1 000 000 AED sur 300 mois, 6 000 AED existants, revenu 40 000 AED | `ok` | endettement total 28,9 % |
| Même client, 15 000 AED existants | `metier` | 51,4 % > 50 % |
| Prêt personnel de 150 000 AED sur 36 mois, revenu 25 000 AED, 3 000 AED existants | `ok` | 29,8 %, montant ≤ 20 salaires |
| Même prêt sur 60 mois | `metier` | 60 > 48 mois |
| 600 000 AED sur 48 mois | `metier` | plus de 20 × 25 000 AED |
| Retraité, pension 20 000 AED, 1 000 AED existants | `metier` | 32,8 % > 30 % |
| `"duree_mois": true` | `schema` | un booléen n'est pas un entier |

### Immobilier — une estimation cohérente avec elle-même

```json
{
  "type": "object",
  "properties": {
    "emirat": {"type": "string", "enum": ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]},
    "quartier": {"type": "string", "minLength": 2, "maxLength": 60},
    "type_bien": {"type": "string", "enum": ["appartement", "villa", "townhouse"]},
    "surface_sqft": {"type": "number", "exclusiveMinimum": 0},
    "prix_aed_sqft": {"type": "number", "exclusiveMinimum": 0},
    "prix_estime_aed": {"type": "number", "exclusiveMinimum": 0},
    "fourchette_aed": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 2, "maxItems": 2},
    "nb_comparables": {"type": "integer", "minimum": 3}
  },
  "required": ["emirat", "quartier", "type_bien", "surface_sqft", "prix_aed_sqft", "prix_estime_aed", "fourchette_aed", "nb_comparables"],
  "additionalProperties": false
}
```

Une agence de Dubaï et d'Abu Dhabi fait produire par un agent des estimations de biens à partir des transactions comparables récentes ; l'estimation est un objet JSON que l'interface affiche et que le conseiller signe avant de l'envoyer au vendeur. Les fonctions s'enchaînent ainsi : `validate`, puis `regles_estimation`, qui vérifie la cohérence interne de l'objet. Un appartement de 1 250 sqft à Dubai Marina, estimé à 1 920 AED/sqft sur 7 comparables, doit valoir 1 250 × 1 920 = 2 400 000 AED et se trouver dans la fourchette [2 250 000 ; 2 550 000] ; l'agent affiche à part les frais de transfert de la DLD, 4 % de la valeur, soit 96 000 AED. Une estimation à 2 600 000 AED avec le même prix au sqft est incohérente : le modèle a corrigé un nombre sans recalculer l'autre, et la règle la bloque avant qu'elle n'atteigne le client. L'émirat écrit « Dubaï », avec un accent, est refusé par l'énumération : la bonne réponse est de normaliser les noms (accents, translittérations, abréviations comme DXB) avant la validation, et non d'élargir l'énumération à toutes les variantes. Avec moins de trois comparables, seuil illustratif fixé par l'agence, l'estimation n'est pas publiée, faute de base suffisante. Sans ces contrôles, une fiche dont le prix total contredit le prix au sqft ruinerait la crédibilité de l'agence et la fragiliserait en cas de litige avec un vendeur. On suit l'écart relatif entre l'estimation et le prix de vente finalement enregistré, avec le critère de 10 % de l'étape 65.

| Instance | Verdict | Motif |
|---|---|---|
| 1 250 sqft à 1 920 AED/sqft, estimé 2 400 000 AED | `ok` | 1 250 × 1 920 = 2 400 000 |
| `"emirat": "Dubaï"` | `schema` | hors de l'énumération |
| `"surface_sqft": 0` | `schema` | la surface doit être > 0 |
| `"prix_estime_aed": 2600000` | `metier` | ≠ 2 400 000 |
| `"nb_comparables": 2` | `schema` | minimum 3 |

### Crypto — un ordre de swap qui ne cache pas son glissement

```json
{
  "type": "object",
  "properties": {
    "adresse_pool": {"type": "string", "pattern": "^0x[0-9a-fA-F]{40}$"},
    "quantite_eth": {"type": "number", "exclusiveMinimum": 0},
    "prix_reference_aed": {"type": "number", "exclusiveMinimum": 0},
    "slippage_max": {"type": "number", "minimum": 0, "maximum": 0.05},
    "montant_min_recu_aed": {"type": "number", "exclusiveMinimum": 0}
  },
  "required": ["adresse_pool", "quantite_eth", "prix_reference_aed", "slippage_max", "montant_min_recu_aed"],
  "additionalProperties": false
}
```

Une plateforme d'actifs virtuels agréée par la VARA laisse un agent préparer les ordres d'échange de ses clients sur des pools de liquidité audités ; l'ordre part ensuite vers le moteur d'exécution, qui ne relit pas l'intention du client. Les fonctions s'enchaînent ainsi : `validate` (adresse au motif `^0x[0-9a-fA-F]{40}$`, glissement maximal dans [0 ; 0,05]), puis `regles_swap`, qui vérifie la liste blanche des pools et la cohérence du montant minimum. Pour vendre 2 ETH à un prix de référence de 12 000 AED, prix illustratif, avec un glissement maximal de 1 %, le montant minimum reçu doit valoir 2 × 12 000 × 0,99 = 23 760 AED. Un ordre qui annonce 1 % mais fixe le minimum à 20 000 AED cache un glissement réel de 1 − 20 000 / 24 000 = 16,7 % ; la règle le refuse, parce que c'est le minimum, et non le pourcentage affiché, que le moteur exécute. Un glissement écrit 0,5 au lieu de 0,005 (le modèle pensait « 0,5 % ») est refusé dès le schéma, car 0,5 > 0,05 ; or le schéma envoyé à l'API en mode strict ne porte pas cette borne (étape 8) : la grammaire garantit le motif de l'adresse, et seule la validation locale arrête le glissement. Sans ces deux niveaux, un seul ordre mal formé pourrait céder la moitié de sa valeur au premier mouvement du marché. La plateforme doit pouvoir montrer à la VARA les contrôles appliqués avant chaque ordre : le verdict et son motif sont journalisés avec l'ordre. On suit le nombre d'ordres bloqués par motif, avec un objectif ferme de zéro ordre exécuté hors bornes.

| Instance | Verdict | Motif |
|---|---|---|
| 2 ETH, prix 12 000 AED, glissement 0,01, minimum 23 760 AED | `ok` | 2 × 12 000 × 0,99 |
| `"slippage_max": 0.5` | `schema` | 0,5 > 0,05 |
| adresse de 39 caractères hexadécimaux | `schema` | motif non respecté |
| `"montant_min_recu_aed": 20000` | `metier` | glissement réel 16,7 % |
| pool absent de la liste blanche | `metier` | pool non audité |

### Assurance — une déclaration de sinistre datée correctement

```json
{
  "type": "object",
  "properties": {
    "numero_police": {"type": "string", "pattern": "^POL-[0-9]{6}$"},
    "date_sinistre": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "date_declaration": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "emirat": {"type": "string", "enum": ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]},
    "montant_dommage_aed": {"type": "number", "minimum": 0},
    "franchise_aed": {"type": "number", "minimum": 0},
    "vetuste": {"type": "number", "minimum": 0, "maximum": 1}
  },
  "required": ["numero_police", "date_sinistre", "date_declaration", "emirat", "montant_dommage_aed", "franchise_aed", "vetuste"],
  "additionalProperties": false
}
```

Un assureur auto et santé reçoit les déclarations d'accident par conversation, en arabe ou en anglais ; l'agent les structure avant qu'un gestionnaire ne calcule l'indemnité avec l'outil de l'étape 12. Les fonctions s'enchaînent ainsi : `validate` (dates au format AAAA-MM-JJ, montants positifs ou nuls, vétusté dans [0 ; 1]), puis `regles_sinistre`, qui lit les deux dates avec `date.fromisoformat` et les compare. Un sinistre survenu le 12 mars 2026 à Sharjah et déclaré le 14 passe ; la même déclaration datée du 10 est refusée, parce qu'un sinistre ne peut pas être déclaré avant d'être survenu, ce qui trahit une erreur de saisie et, parfois, une tentative de fraude. Le 30 février 2026 respecte le motif `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` mais n'existe pas : seul `date.fromisoformat` le détecte, preuve qu'un motif vérifie la forme et pas le sens. Une franchise de −500 AED est refusée par le schéma, parce qu'elle augmenterait l'indemnité au lieu de la réduire, et la date « 12/03/2026 » l'est aussi, parce qu'elle peut se lire 12 mars ou 3 décembre. Sans ces contrôles, l'indemnité serait calculée sur une période où la police n'était peut-être pas en vigueur, et la fraude par antidatage passerait inaperçue. L'assurance étant supervisée par la CBUAE, chaque correction apportée au dossier est journalisée avec son auteur. On suit le taux de déclarations qu'un gestionnaire doit ressaisir et le nombre de dates incohérentes par semaine.

| Instance | Verdict | Motif |
|---|---|---|
| sinistre le 2026-03-12, déclaré le 2026-03-14 | `ok` | ordre des dates respecté |
| déclaré le 2026-03-10 | `metier` | déclaré avant d'être survenu |
| `"date_sinistre": "2026-02-30"` | `metier` | date inexistante |
| `"date_sinistre": "12/03/2026"` | `schema` | motif non respecté |
| `"franchise_aed": -500` | `schema` | minimum 0 |

### RH — une fiche d'embauche conforme

```json
{
  "type": "object",
  "properties": {
    "emirates_id": {"type": "string", "pattern": "^784-[0-9]{4}-[0-9]{7}-[0-9]$"},
    "nationalite": {"type": "string", "pattern": "^[A-Z]{2}$"},
    "salaire_base_aed": {"type": "number", "exclusiveMinimum": 0},
    "salaire_total_aed": {"type": "number", "exclusiveMinimum": 0},
    "emirat_travail": {"type": "string", "enum": ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]},
    "zone": {"type": "string", "enum": ["hors_DIFC", "DIFC"]},
    "regime_fin_de_service": {"type": "string", "enum": ["gratuite_33_2021", "pension_nationaux", "epargne_dews"]}
  },
  "required": ["emirates_id", "nationalite", "salaire_base_aed", "salaire_total_aed", "emirat_travail", "zone", "regime_fin_de_service"],
  "additionalProperties": false
}
```

Un cabinet RH multi-émirats prépare pour ses clients les dossiers d'embauche : contrat, enregistrement auprès du MOHRE, paie par le système de protection des salaires (WPS) et droits de fin de service. Les fonctions s'enchaînent ainsi : `validate` (Emirates ID au format `784-AAAA-NNNNNNN-C`, nationalité sur deux lettres majuscules, salaires strictement positifs), puis `regles_embauche`, qui rappelle `emirates_id_format_valide` du code canonique, cherche la nationalité dans la liste ISO 3166-1, compare le salaire de base au salaire total et contrôle le régime de fin de service. Le code « UK » passe le motif `^[A-Z]{2}$` mais n'est pas un code ISO 3166-1 alpha-2 attribué : le Royaume-Uni s'écrit GB, et le dossier serait rejeté par le système destinataire. Le salaire de base, qui sert au calcul de l'indemnité de fin de service, ne peut pas dépasser le salaire total : pour 10 000 AED de base et sept ans de service, cette indemnité vaut 55 000 AED (étape 13). Un salarié émirien ne relève pas de la gratuité du décret-loi fédéral 33/2021 mais du régime de retraite des nationaux (GPSSA au niveau fédéral), et un salarié du DIFC relève du régime d'épargne DEWS : la règle impose cette cohérence entre la nationalité, la zone et le régime. Le contrôle métier rattrape enfin le saut de ligne final que le motif Python laisse passer (étape 8), puisque `emirates_id_format_valide` refuse tout caractère qui n'est pas un chiffre. On suit le nombre de rejets de paie WPS imputables à une fiche mal remplie, avec un objectif de zéro.

| Instance | Verdict | Motif |
|---|---|---|
| salarié de nationalité IN, base 10 000 AED, total 15 000 AED, Dubai, hors DIFC | `ok` | régime de gratuité attendu |
| `"nationalite": "UK"` | `metier` | code non attribué (le Royaume-Uni est GB) |
| `"nationalite": "in"` | `schema` | minuscules refusées par le motif |
| base 16 000 AED pour un total de 15 000 AED | `metier` | base > total |
| `"nationalite": "AE"` au régime de gratuité | `metier` | régime de retraite des nationaux attendu |
| zone DIFC au régime d'épargne DEWS | `ok` | régime cohérent |

### BTP — une facture de sous-traitant payable

```json
{
  "type": "object",
  "properties": {
    "numero_facture": {"type": "string", "pattern": "^FAC-[0-9]{4}-[0-9]{5}$"},
    "montant_ht_aed": {"type": "number", "exclusiveMinimum": 0},
    "tva_aed": {"type": "number", "minimum": 0},
    "ttc_aed": {"type": "number", "exclusiveMinimum": 0},
    "iban": {"type": "string", "pattern": "^AE[0-9]{21}$"}
  },
  "required": ["numero_facture", "montant_ht_aed", "tva_aed", "ttc_aed", "iban"],
  "additionalProperties": false
}
```

Un groupe de construction qui mène de grands chantiers à Dubaï reçoit chaque mois des centaines de factures de sous-traitants en PDF ; l'agent les lit, les structure et prépare leur mise en paiement. Les fonctions s'enchaînent ainsi : `validate` (numéro de facture, montants, IBAN compact au motif `^AE[0-9]{21}$`), puis `regles_facture`, qui vérifie la clé mod 97 avec `iban_ae_valide`, la TVA à 5 % du HT avec `tva`, et l'écart entre le TTC et HT × 1,05, au plus 0,01 AED. Une facture de 120 000 AED HT, 6 000 AED de TVA et 126 000 AED TTC passe ; une facture de 12 345,67 AED HT dont la TVA exacte, 617,2835 AED, a été arrondie au fils (1 AED = 100 fils) à 617,28 AED donne un TTC de 12 962,95 AED, à 0,0035 AED du produit exact, et passe aussi grâce à la tolérance. Un TTC de 126 500 AED, 500 AED trop haut, est bloqué ; un IBAN `AE08…` qui ne diffère du bon que par sa clé respecte le motif mais pas le mod 97, et il est arrêté avant tout virement (démonstration, point 4). Un IBAN saisi avec ses espaces est refusé par le schéma : l'agent doit normaliser la saisie avant de valider, et garder la valeur brute pour l'audit. La tolérance de 0,01 AED suppose une TVA arrondie une seule fois : une facture de 40 lignes arrondies une par une peut s'écarter de 0,20 AED en restant juste, et la règle doit alors être adaptée (démonstration, point 3). La TVA relève de l'autorité fiscale fédérale ; on suit le taux de factures rejetées par sous-traitant, qui révèle aussi les modèles de facture que l'agent lit mal.

| Instance | Verdict | Motif |
|---|---|---|
| HT 120 000 AED, TVA 6 000 AED, TTC 126 000 AED, IBAN `AE07…` | `ok` | mod 97 = 1, écart nul |
| HT 12 345,67 AED, TVA 617,28 AED, TTC 12 962,95 AED | `ok` | écart 0,0035 AED ≤ 0,01 |
| TTC 126 500 AED | `metier` | écart 500 AED |
| IBAN `AE08…` | `metier` | clé mod 97 fausse |
| IBAN écrit avec des espaces | `schema` | forme compacte attendue |

## Démonstration

### 1. La mensualité d'un prêt amortissable

On emprunte un capital P au taux mensuel r et l'on rembourse n mensualités égales M. Le prêt est remboursé exactement quand la valeur actuelle des mensualités égale le capital, parce qu'un dirham placé au taux r pendant k mois devient (1+r)ᵏ dirhams : la mensualité payée au mois k vaut donc aujourd'hui M / (1+r)ᵏ.

$$
P = \sum_{k=1}^{n} \frac{M}{(1+r)^{k}} = M \sum_{k=1}^{n} q^{k} \qquad \text{avec} \qquad q = \frac{1}{1+r}
$$

La somme est une série géométrique. Si S = q + q² + … + qⁿ, alors qS = q² + … + qⁿ⁺¹, et la soustraction donne S − qS = q − qⁿ⁺¹, d'où S = q (1 − qⁿ)/(1 − q). Comme 1 − q = r/(1+r), on a q/(1−q) = 1/r, et donc :

$$
P = M\,\frac{1-(1+r)^{-n}}{r}
\qquad\Longleftrightarrow\qquad
M = \frac{P\,r}{1-(1+r)^{-n}}
$$

Avec P = 1 000 000 AED, r = 0,045/12 = 0,00375 et n = 300 : (1,00375)³⁰⁰ = 3,07374, donc (1,00375)⁻³⁰⁰ = 0,32534 et M = 3 750 / 0,67466 = 5 558,32 AED. Quand le taux tend vers 0, (1+r)⁻ⁿ = 1 − nr + o(r), donc le dénominateur vaut nr + o(r) et M tend vers P/n : c'est la branche `principal / n_mois` du code (120 000 AED sur 24 mois à taux nul donnent 5 000 AED). Le programme vérifie aussi la définition elle-même : la somme des 300 mensualités actualisées redonne 1 000 000 AED.

### 2. Pourquoi l'endettement se calcule sur le total

Notons D les mensualités existantes, M la nouvelle mensualité et R le revenu mensuel. Le plafond de la CBUAE porte sur le taux d'endettement total :

$$
E = \frac{D + M}{R} \le 0{,}50
$$

Le contre-exemple chiffré montre ce que coûte l'oubli de D : avec D = 15 000, M = 5 558,32 et R = 40 000, le rapport M/R vaut 13,9 % et passerait largement, alors que E vaut 51,4 % et dépasse le plafond. Comme E croît avec D, la dette existante maximale compatible avec ce prêt s'obtient en résolvant E = 0,5 :

$$
D_{max} = 0{,}5\,R - M = 20\,000 - 5\,558{,}32 = 14\,441{,}68
$$

AED. Un client qui rembourse déjà 14 000 AED par mois reste recevable ; à 14 500 AED, il ne l'est plus.

### 3. Une tolérance de 0,01 AED, et sa limite

Un montant arrondi au fils diffère du montant exact d'au plus un demi-fils : | arr(x) − x | ≤ 0,005 AED. Si la facture arrondit la TVA une seule fois, sur le total, avec T = arr(0,05 H) et TTC = H + T, alors :

$$
\lvert \text{TTC} - 1{,}05\,H \rvert = \lvert T - 0{,}05\,H \rvert \le 0{,}005
$$

Une tolérance de 0,01 AED accepte donc cet arrondi avec une marge d'un facteur 2, et rien de plus : un écart de 500 AED, comme le TTC à 126 500 AED, vaut 50 000 fois la tolérance. Sur l'exemple, 0,05 × 12 345,67 = 617,2835, arrondi à 617,28, et l'écart vaut 0,0035 AED. Si la facture arrondit la TVA **ligne par ligne**, les écarts s'ajoutent : par l'inégalité triangulaire, l'écart total est au plus 0,005 × L pour L lignes. Avec 40 lignes de 100,10 AED HT, chaque TVA exacte de 5,005 AED est arrondie à 5,01 AED, et l'écart total atteint 40 × 0,005 = 0,20 AED : une facture juste serait refusée par la règle à 0,01. La règle correcte est donc une tolérance de 0,005 × L, ou un recalcul selon la convention d'arrondi déclarée par le fournisseur.

### 4. Le mod 97 détecte toute erreur sur un chiffre et toute inversion de deux voisins

Pour contrôler un IBAN, on place les 4 premiers caractères à la fin, on remplace chaque lettre par un nombre (A = 10, E = 14) et l'on obtient un entier N ; l'IBAN est valide si

$$
N \equiv 1 \pmod{97} .
$$

- **Substitution d'un chiffre.** Remplacer le chiffre a par b à la position de poids 10ᵏ change N de (b − a) 10ᵏ, avec 0 < | b − a | ≤ 9. Comme 97 est premier, il ne divise un produit que s'il divise l'un des facteurs ; or il ne divise pas b − a, trop petit, ni 10ᵏ = 2ᵏ 5ᵏ. Le reste modulo 97 change donc, et l'erreur est détectée.
- **Inversion de deux chiffres voisins** a puis b, de poids 10ᵏ⁺¹ et 10ᵏ : la variation vaut

$$
(b - a)\,10^{k+1} + (a - b)\,10^k = 9\,(b - a)\,10^k ,
$$

que 97 ne divise pas pour la même raison.
- **Le seul couple de voisins séparés par le réarrangement** est le second chiffre de contrôle (poids 10⁰) et le premier chiffre du BBAN (poids 10²⁴) : la variation vaut (b − a)(10²⁴ − 1) au signe près, et 97 ne divise pas 10²⁴ − 1, parce que le plus petit k tel que

$$
10^k \equiv 1 \pmod{97}
$$

vaut 96, qui ne divise pas 24.

Le programme l'éprouve sur l'IBAN d'exemple : les 189 substitutions possibles d'un chiffre (21 positions × 9 valeurs) et les 19 inversions de voisins distincts sont toutes refusées.

### 5. Le schéma d'abord : une précondition, pas une formalité

Chaque fonction de règles suppose que ses entrées ont le bon type. Sur `{"duree_mois": "36"}`, la comparaison `"36" <= 0` dans `mensualite` lève `TypeError` en Python 3, et `regles_credit` plante au lieu de rendre un verdict. En validant d'abord, on garantit que les règles ne reçoivent que des instances bien formées : le schéma est la précondition qui rend les règles **totales**, c'est-à-dire définies sur toutes leurs entrées. Le programme vérifie cet échec par un `assert`.

## Le programme

### Déroulé, ligne par ligne

**Le validateur** (`MOTS_CLES` à `validate`) est recopié de l'étape 8 sans aucun changement : son déroulé y est détaillé.

**Les fonctions canoniques** `iban_ae_valide`, `emirates_id_format_valide`, `mensualite`, `ratio_endettement` et `tva` sont recopiées du code commun du parcours. `iban_ae_valide` retire les espaces, vérifie la longueur (23), le préfixe `AE` et les chiffres, déplace les 4 premiers caractères à la fin, convertit chaque caractère en base 36 (`int("A", 36)` vaut 10) et teste le reste modulo 97. `ratio_endettement` additionne **toutes** les mensualités avant de diviser par le revenu.

**`objet(proprietes)`** fabrique un schéma d'objet strict : `required` reçoit la liste de tous les champs, et `additionalProperties` vaut `False`. C'est la forme qu'exige le mode strict de l'API.

**Les six schémas** reprennent exactement les blocs JSON des cas ci-dessus, en syntaxe Python (`False` au lieu de `false`).

**Les fonctions de règles**, une par domaine, renvoient une liste d'erreurs au même format que `validate`, avec un chemin JSON.

- `regles_credit` : pour un prêt personnel, `d["duree_mois"] > 48` et `d["montant_aed"] > 20 * d["revenu_mensuel_aed"]` ; puis `plafond = 0.30 if d["retraite"] else 0.50`, et `ratio_endettement` avec ce plafond. Pour le dossier à 15 000 AED existants, `ratio` vaut 0,51396 et le message affiche `51.4%`.
- `regles_estimation` : `attendu = 1250 * 1920 = 2400000` ; une estimation à 2 600 000 s'en écarte de 200 000 AED, bien plus que la tolérance de 1 AED. La ligne `bas, haut = d["fourchette_aed"]` est sûre, parce que le schéma impose exactement deux éléments.
- `regles_swap` : `plancher = 2 * 12000 * (1 - 0.01) = 23760` ; pour un minimum de 20 000 AED, `cache = 1 - 20000 / 24000 = 0.1667`, le glissement réel affiché dans le message. `.lower()` compare l'adresse sans tenir compte de la casse, que le motif autorise.
- `regles_sinistre` : `date.fromisoformat("2026-02-30")` lève `ValueError`, transformée en erreur métier ; sinon, `survenu > declare` compare deux objets `date`.
- `regles_embauche` : quatre contrôles, dont le choix du régime attendu par une cascade `if`/`elif`/`else` : `"AE"` donne `pension_nationaux`, la zone `DIFC` donne `epargne_dews`, et tout autre cas `gratuite_33_2021`.
- `regles_facture` : `tva(120000)` vaut 6 000 et `abs(126000 - 120000 * 1.05)` vaut 0 ; pour un TTC de 126 500, l'écart vaut 500, et la facture est bloquée.

**`controler(instance, schema, regles)`** applique la méthode : si `validate` trouve des erreurs, la fonction renvoie `("schema", erreurs)` sans appeler les règles ; sinon elle renvoie `("metier", erreurs)` ou `("ok", [])`.

**`essayer(titre, instance, schema, regles, attendu)`** affiche une ligne de trace, avec la première erreur s'il y en a une, et vérifie par `assert` que le verdict est celui attendu.

**`main()`**, section par section.

1. Banque : la mensualité de 5 558,32 AED et le taux de 28,9 % sont vérifiés, ainsi que chaque nombre de la démonstration : r = 0,00375, (1+r)³⁰⁰ = 3,07374, la somme actualisée des 300 mensualités, le cas du taux nul et Dₘₐₓ = 14 441,68 AED. Sept dossiers suivent, puis la preuve, par `TypeError`, que les règles plantent sans le schéma.
2. Immobilier : cinq instances ; les frais DLD de 96 000 AED sont vérifiés à part.
3. Crypto : cinq instances ; le glissement caché de 16,7 % est vérifié dans le message.
4. Assurance : cinq instances, dont le 30 février.
5. RH : six instances ; les deux dernières lignes montrent que le motif Python accepte un saut de ligne final, et que `emirates_id_format_valide` le refuse.
6. BTP : cinq instances, dont la facture arrondie au fils ; puis le calcul en fils de la facture de 40 lignes, où `(10010 * 5 + 50) // 100` arrondit 500,5 fils à 501 fils, ce qui donne un écart de 20 fils, soit 0,20 AED.
7. Mod 97 : la liste `variantes` contient les 189 IBAN obtenus en changeant un seul chiffre, la liste `inversions` les 19 IBAN obtenus en échangeant deux chiffres voisins différents ; aucun n'est accepté.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`type_json(x)`** — C'est la même fonction que dans le programme de l'étape 8 : l'officier d'état civil reçoit une valeur Python et renvoie son nom JSON, `"null"`, `"boolean"`, `"integer"`, `"number"`, `"string"`, `"array"` ou `"object"`, en testant les booléens avant les entiers, puisque `True` est aussi un `int` en Python. Toute valeur sans équivalent JSON, comme un tuple, lève `ValueError`. Ici, elle sert au validateur pour écrire le type reçu dans les messages, par exemple quand une durée booléenne est refusée dans le dossier de crédit.

**`entier_json(x)`** — Reprise telle quelle de l'étape 8, cette fonction est le contrôleur qui ne reconnaît comme entier que ce qu'un document JSON appellerait ainsi : elle reçoit une valeur, renvoie `None` pour un booléen, l'entier lui-même pour un `int`, sa conversion en `int` pour un flottant sans partie décimale comme 36.0, et `None` pour tout le reste, y compris 36.5 ou la chaîne `"36"`. Elle ne lève rien. C'est elle qui fait refuser par le schéma de crédit la durée `True`, qu'un test naïf aurait acceptée comme un entier.

**`correspond(x, nom)`** — Même fonction que dans le programme de l'étape 8 : comme un portier qui compare un badge à la liste des accès, elle reçoit une valeur et un nom de type JSON, délègue à `entier_json` pour `"integer"`, accepte les entiers comme les décimaux pour `"number"`, puisque tout entier est un nombre, et compare simplement `type_json(x)` au nom attendu dans les autres cas. Elle renvoie ce booléen, que `validate` consulte pour chaque type admis par le schéma, comme `"number"` pour la surface d'un bien.

**`egal_json(a, b)`** — Reprise de l'étape 8, cette fonction est l'arbitre qui compare deux valeurs comme le ferait JSON et non comme le fait Python : elle reçoit deux valeurs et renvoie vrai seulement si elles sont toutes deux booléennes ou toutes deux non booléennes, et égales au sens de `==`. Ainsi `False` n'égale pas 0, alors que 1.0 égale bien 1. Elle ne lève rien ; `validate` s'en sert pour les énumérations, ce qui fait refuser, dans ce fichier, l'émirat « Dubaï » accentué, absent de la liste `EMIRATS`.

**`validate(instance, schema, path)`** — C'est le validateur de l'étape 8, recopié sans changement : l'inspecteur reçoit une instance, un schéma et un chemin, `"$"` par défaut, refuse par `ValueError` tout mot-clé qu'il ne sait pas vérifier, renvoie aussitôt une seule erreur si le type ne correspond pas, puis contrôle énumérations, bornes, longueurs, motifs, tableaux et objets en se rappelant lui-même sur chaque champ et chaque élément. Il renvoie la liste des erreurs, préfixées par leur chemin, vide si l'instance est bien formée ; ici, c'est la première porte de `controler`, avant toute règle métier.

**`iban_ae_valide(iban)`** — Cette fonction commune du parcours est le guichetier qui vérifie un numéro de compte avant de payer un sous-traitant : elle reçoit un IBAN, retire les espaces et passe en majuscules, renvoie `False` si le numéro ne fait pas 23 caractères, ne commence pas par AE ou contient autre chose que des chiffres ensuite, puis déplace les quatre premiers caractères à la fin, convertit chaque caractère en base 36 et vérifie que le nombre obtenu vaut 1 modulo 97. Elle renvoie ce booléen : l'IBAN « AE070331234567890123456 » passe, sa variante à clé « AE08 » échoue, et aucune des 189 substitutions ni des 19 inversions de la septième section n'est acceptée.

**`emirates_id_format_valide(eid)`** — Celle-ci est l'huissier qui contrôle le gabarit d'une carte d'identité sans l'authentifier : elle reçoit un numéro, en retire tirets et espaces, et renvoie `True` seulement s'il reste exactement 15 chiffres commençant par 784, sans calculer de clé. Elle sert de second contrôle dans `regles_embauche`, et c'est là qu'elle rattrape ce que le motif du schéma laisse passer : en Python, le `$` du motif accepte un saut de ligne final, alors que « 784-1990-1234567-1 » suivi d'un saut de ligne n'a plus 15 chiffres purs et est refusé.

**`mensualite(principal, taux_annuel, n_mois)`** — C'est le calculateur du banquier, commun à tout le parcours : il reçoit le capital, le taux annuel et la durée en mois, lève `ValueError` si le capital ou la durée ne sont pas positifs ou si le taux est négatif, et renvoie P r / (1 − (1 + r)⁻ⁿ) avec le taux mensuel r, ou P / n si le taux est nul. Pour l'hypothèque de 1 000 000 AED à 4,5 % sur 300 mois, il donne 5 558,32 AED ; pour 120 000 AED à taux nul sur 24 mois, 5 000 AED. Comme il compare la durée à 0, une durée écrite en texte, `"36"`, le fait planter par `TypeError`, ce que `main` vérifie.

**`ratio_endettement(mensualites_existantes, nouvelle_mensualite, revenu_mensuel, plafond)`** — Cette fonction commune est l'analyste qui met toutes les charges du client dans un plateau de la balance et son revenu dans l'autre : elle reçoit les mensualités en cours, la nouvelle, le revenu et un plafond, 0,50 par défaut, lève `ValueError` si le revenu n'est pas positif et renvoie le couple formé du ratio et d'un booléen de conformité. Avec 6 000 AED de dettes, 5 558,32 AED de nouvelle mensualité et 40 000 AED de revenu, le ratio vaut 28,9 % ; `regles_credit` lui passe un plafond de 0,30 pour un retraité.

**`tva(montant_ht, taux)`** — Même fonction commune que dans les programmes précédents, le percepteur sobre qui renvoie le produit d'un montant hors taxes par un taux, 0,05 par défaut, sans arrondi ni contrôle. Dans ce fichier, `regles_facture` l'appelle pour recalculer la TVA attendue, 6 000 AED sur une facture de 120 000 AED hors taxes, et `main` l'utilise pour construire la facture de 12 345,67 AED dont la TVA est arrondie au fils, qui doit pourtant passer les contrôles avec un total de 12 962,95 AED.

**`objet(proprietes)`** — Cette petite fonction est le notaire qui rédige un contrat sans clause facultative : elle reçoit un dictionnaire de propriétés, chacune avec son sous-schéma, et renvoie un schéma d'objet dans lequel `required` contient la liste de tous les champs et `additionalProperties` vaut `False`. Elle ne lève rien et ne vérifie pas les sous-schémas. C'est la forme stricte qu'exige l'API en mode strict ; les six schémas du fichier, du crédit à la facture, sont tous construits avec elle, si bien qu'un champ manquant ou inattendu est toujours refusé par `validate`.

**`regles_credit(d)`** — C'est l'analyste crédit qui applique, sur un dossier déjà bien formé, les règles qu'un schéma ne sait pas exprimer : il reçoit le dictionnaire validé et, pour un prêt personnel, signale une durée de plus de 48 mois ou un montant de plus de 20 fois le salaire mensuel ; il calcule ensuite la mensualité, choisit un plafond de 30 % pour un retraité et de 50 % sinon, puis signale un endettement total qui le dépasse. Il renvoie la liste des erreurs, au même format que `validate` : vide pour l'hypothèque avec 6 000 AED de dettes, un endettement de 51,4 % avec 15 000 AED, et 32,8 % pour le retraité.

**`regles_estimation(d)`** — Celle-ci est l'expert immobilier qui refait la multiplication avant de signer le rapport : elle reçoit une estimation validée, recalcule surface × prix au sqft et signale un prix estimé qui s'en écarte de plus de 1 AED, puis vérifie que le prix estimé tombe dans sa propre fourchette, dont le schéma garantit qu'elle a exactement deux bornes. Elle renvoie la liste des erreurs : aucune pour 1 250 sqft à 1 920 AED, soit 2 400 000 AED dans la fourchette de 2 250 000 à 2 550 000 AED, mais une incohérence quand le prix annoncé passe à 2 600 000 AED.

**`regles_swap(d)`** — Cette fonction est le contrôleur des risques d'une plateforme d'échange qui relit l'ordre avant de l'envoyer : elle reçoit un ordre de swap validé, signale un pool dont l'adresse, comparée en minuscules, n'est pas dans la liste blanche `POOLS_AUDITES`, puis recalcule le plancher quantité × prix × (1 − glissement maximal) et signale un minimum reçu qui s'en écarte de plus d'un centième, en affichant le glissement réellement caché. Elle renvoie la liste des erreurs : rien pour 2 ETH à 12 000 AED avec 1 %, soit 23 760 AED, mais un glissement réel de 16,7 % quand le minimum tombe à 20 000 AED.

**`regles_sinistre(d)`** — Celle-ci est le gestionnaire de sinistres qui vérifie que le calendrier tient debout : elle reçoit une déclaration validée, convertit les deux dates avec `date.fromisoformat` et, si l'une n'existe pas, comme le 30 février que le motif du schéma laisse passer, renvoie une erreur « date inexistante » au lieu de laisser sortir le `ValueError`. Sinon, elle renvoie une erreur si le sinistre est postérieur à sa déclaration, et une liste vide dans le cas normal, comme le sinistre du 12 mars déclaré le 14.

**`regles_embauche(d)`** — C'est le juriste RH qui vérifie un contrat d'embauche validé sur quatre points : il recontrôle le format de l'Emirates ID, exige un code de nationalité présent dans l'extrait ISO 3166-1 du programme, refuse un salaire de base supérieur au salaire total, puis déduit le régime de fin de service attendu, pension des nationaux pour la nationalité AE, épargne DEWS pour la zone DIFC et gratuité du décret-loi 33/2021 sinon, et signale tout autre régime déclaré. Il renvoie la liste des erreurs : vide pour le salarié indien à Dubaï, mais une erreur pour le code « UK », pour une base de 16 000 AED sur 15 000 et pour un Émirien placé au régime de gratuité.

**`regles_facture(d)`** — Cette fonction est le comptable fournisseurs qui pointe la facture d'un sous-traitant avant paiement : elle reçoit une facture validée, signale un IBAN dont la clé modulo 97 est fausse, une TVA qui s'écarte de plus d'un centième des 5 % recalculés par `tva`, et un total TTC qui s'écarte de plus d'un centième de HT × 1,05. Elle renvoie la liste des erreurs : aucune pour 120 000 AED hors taxes, 6 000 AED de TVA et 126 000 AED TTC, mais un écart de 500 AED quand le TTC passe à 126 500 AED, et une clé invalide pour l'IBAN commençant par AE08.

**`controler(instance, schema, regles)`** — C'est l'aiguilleur qui impose l'ordre des contrôles, le schéma d'abord et le métier ensuite : il reçoit une instance, un schéma et la fonction de règles du domaine, appelle `validate` et, s'il y a des erreurs, renvoie aussitôt le couple `("schema", erreurs)` sans jamais appeler les règles, qui pourraient planter sur une entrée mal typée. Sinon, il applique les règles et renvoie `("metier", erreurs)` s'il en trouve, ou `("ok", [])`. Ce verdict en trois valeurs est celui que chaque ligne de `main` compare au résultat attendu.

**`essayer(titre, instance, schema, regles, attendu)`** — Cette fonction est le greffier qui consigne chaque essai sur une ligne et vérifie qu'il finit comme prévu : elle reçoit un titre, une instance, un schéma, des règles et le verdict attendu, appelle `controler`, imprime le titre, une flèche, le verdict et la première erreur s'il y en a une, puis lève `AssertionError` si le verdict diffère de celui attendu. Elle renvoie la liste des erreurs, que `main` réutilise pour vérifier un détail du message, comme les 51,4 % du dossier de crédit ou les 16,7 % de glissement caché.

**`main()`** — C'est le chef de projet qui fait défiler les six domaines et une démonstration finale : il vérifie d'abord les nombres du crédit, mensualité de 5 558,32 AED, ratio de 28,9 %, valeur actuelle des 300 mensualités, dette maximale de 14 441,68 AED, puis sept dossiers et le plantage de la règle sans schéma. Il enchaîne cinq estimations immobilières avec les frais DLD de 96 000 AED, cinq ordres de swap, cinq déclarations de sinistre, six embauches avec le piège du saut de ligne final, cinq factures et l'écart de 0,20 AED de la facture de 40 lignes, et termine par les 189 substitutions et 19 inversions d'IBAN, toutes refusées.

```python
"""Étape 9 — six schémas EAU : instances valides et invalides, règles inter-champs, décision."""
import math
import re
import sys
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- validateur de l'étape 8 (recopié sans changement)
MOTS_CLES = {"type", "enum", "properties", "required", "additionalProperties", "items", "minItems", "maxItems",
             "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength", "pattern"}
ANNOTATIONS = {"title", "description", "default", "examples", "$schema"}


def type_json(x) -> str:
    """Nom JSON d'une valeur Python. bool est testé AVANT int, parce que isinstance(True, int) est vrai."""
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "boolean"
    if isinstance(x, int):
        return "integer"
    if isinstance(x, float):
        return "number"
    if isinstance(x, str):
        return "string"
    if isinstance(x, list):
        return "array"
    if isinstance(x, dict):
        return "object"
    raise ValueError(f"valeur sans équivalent JSON : {type(x).__name__}")


def entier_json(x) -> int | None:
    """L'entier que représente x (36 ou 36.0), ou None si x n'est pas un entier JSON (True, 36.5, "36")."""
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return None


def correspond(x, nom: str) -> bool:
    if nom == "integer":
        return entier_json(x) is not None
    if nom == "number":
        return type_json(x) in ("integer", "number")
    return type_json(x) == nom


def egal_json(a, b) -> bool:
    """Égalité au sens JSON : true n'est pas 1, alors qu'en Python True == 1 est vrai."""
    return isinstance(a, bool) == isinstance(b, bool) and a == b


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Liste des erreurs, chacune préfixée par son chemin JSON ($.garanties[0]) ; liste vide = instance valide."""
    inconnus = set(schema) - MOTS_CLES - ANNOTATIONS
    if inconnus:
        raise ValueError(f"mots-clés non pris en charge : {sorted(inconnus)}")   # refuser plutôt qu'ignorer
    if "type" in schema:
        attendus = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(correspond(instance, t) for t in attendus):
            noms = " ou ".join(attendus)
            return [f"{path} : type attendu {noms}, reçu {type_json(instance)}"]
    erreurs = []
    if "enum" in schema and not any(egal_json(instance, v) for v in schema["enum"]):
        erreurs.append(f"{path} : {instance!r} hors de l'énumération {schema['enum']}")
    t = type_json(instance)
    if t in ("integer", "number"):
        if not math.isfinite(instance):
            return erreurs + [f"{path} : nombre non fini ({instance}), interdit en JSON"]
        if "minimum" in schema and instance < schema["minimum"]:
            erreurs.append(f"{path} : {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            erreurs.append(f"{path} : {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            erreurs.append(f"{path} : {instance} doit être > {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and instance >= schema["exclusiveMaximum"]:
            erreurs.append(f"{path} : {instance} doit être < {schema['exclusiveMaximum']}")
    elif t == "string":
        if "minLength" in schema and len(instance) < schema["minLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            erreurs.append(f"{path} : {instance!r} ne respecte pas le motif {schema['pattern']}")
    elif t == "array":
        if "minItems" in schema and len(instance) < schema["minItems"]:
            erreurs.append(f"{path} : {len(instance)} élément(s) < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            erreurs.append(f"{path} : {len(instance)} élément(s) > maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, element in enumerate(instance):
                erreurs += validate(element, schema["items"], f"{path}[{i}]")
    elif t == "object":
        proprietes = schema.get("properties", {})
        supplementaires = schema.get("additionalProperties", True)
        if not isinstance(supplementaires, bool):
            raise ValueError("additionalProperties : seuls true et false sont pris en charge ici")
        for cle in schema.get("required", []):
            if cle not in instance:
                erreurs.append(f"{path} : champ obligatoire absent « {cle} »")
        for cle, valeur in instance.items():
            if cle in proprietes:
                erreurs += validate(valeur, proprietes[cle], f"{path}.{cle}")
            elif not supplementaires:
                erreurs.append(f"{path} : champ non prévu « {cle} »")
    return erreurs


# ---------------------------------------------------------------- fonctions canoniques du parcours (recopiées)
def iban_ae_valide(iban: str) -> bool:
    """IBAN émirien : 23 caractères, « AE », puis 21 chiffres ; contrôle ISO 13616 mod 97 = 1."""
    s = iban.replace(" ", "").upper()
    if len(s) != 23 or not s.startswith("AE") or not s[2:].isdigit():
        return False
    reorganise = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in reorganise)) % 97 == 1


def emirates_id_format_valide(eid: str) -> bool:
    """Format seulement : 15 chiffres commençant par 784 (affiché 784-AAAA-NNNNNNN-C). Pas de contrôle de clé ici."""
    chiffres = eid.replace("-", "").replace(" ", "")
    return len(chiffres) == 15 and chiffres.isdigit() and chiffres.startswith("784")


def mensualite(principal: float, taux_annuel: float, n_mois: int) -> float:
    """M = P r / (1 - (1 + r)^-n), r = taux mensuel ; M = P / n si le taux est nul."""
    if principal <= 0 or n_mois <= 0 or taux_annuel < 0:
        raise ValueError("principal > 0, n_mois > 0, taux >= 0")
    r = taux_annuel / 12
    return principal / n_mois if r == 0 else principal * r / (1 - (1 + r) ** -n_mois)


def ratio_endettement(mensualites_existantes: float, nouvelle_mensualite: float, revenu_mensuel: float,
                      plafond: float = 0.50) -> tuple[float, bool]:
    """Ratio d'endettement CBUAE : TOUTES les mensualités (existantes + nouvelle) / revenu ; plafond 50 % (30 % retraité)."""
    if revenu_mensuel <= 0:
        raise ValueError("revenu > 0")
    ratio = (mensualites_existantes + nouvelle_mensualite) / revenu_mensuel
    return ratio, ratio <= plafond


def tva(montant_ht: float, taux: float = 0.05) -> float:
    """TVA standard des EAU : 5 %. (Loyer résidentiel exonéré ; première livraison d'un bien résidentiel au taux zéro.)"""
    return montant_ht * taux


# ---------------------------------------------------------------- les six contrats
EMIRATS = ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]
MOTIF_EID = "^784-[0-9]{4}-[0-9]{7}-[0-9]$"
MOTIF_DATE = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"


def objet(proprietes: dict) -> dict:
    """Objet strict : tous les champs obligatoires, aucun champ non prévu."""
    return {"type": "object", "properties": proprietes, "required": list(proprietes), "additionalProperties": False}


SCHEMA_CREDIT = objet({
    "type_pret": {"type": "string", "enum": ["hypothecaire", "personnel"]},
    "montant_aed": {"type": "number", "exclusiveMinimum": 0},
    "taux_annuel": {"type": "number", "minimum": 0, "maximum": 0.3},
    "duree_mois": {"type": "integer", "minimum": 12, "maximum": 300},
    "revenu_mensuel_aed": {"type": "number", "exclusiveMinimum": 0},
    "mensualites_existantes_aed": {"type": "number", "minimum": 0},
    "retraite": {"type": "boolean"},
})

SCHEMA_ESTIMATION = objet({
    "emirat": {"type": "string", "enum": EMIRATS},
    "quartier": {"type": "string", "minLength": 2, "maxLength": 60},
    "type_bien": {"type": "string", "enum": ["appartement", "villa", "townhouse"]},
    "surface_sqft": {"type": "number", "exclusiveMinimum": 0},
    "prix_aed_sqft": {"type": "number", "exclusiveMinimum": 0},
    "prix_estime_aed": {"type": "number", "exclusiveMinimum": 0},
    "fourchette_aed": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 2, "maxItems": 2},
    "nb_comparables": {"type": "integer", "minimum": 3},
})

SCHEMA_SWAP = objet({
    "adresse_pool": {"type": "string", "pattern": "^0x[0-9a-fA-F]{40}$"},
    "quantite_eth": {"type": "number", "exclusiveMinimum": 0},
    "prix_reference_aed": {"type": "number", "exclusiveMinimum": 0},
    "slippage_max": {"type": "number", "minimum": 0, "maximum": 0.05},
    "montant_min_recu_aed": {"type": "number", "exclusiveMinimum": 0},
})

SCHEMA_SINISTRE = objet({
    "numero_police": {"type": "string", "pattern": "^POL-[0-9]{6}$"},
    "date_sinistre": {"type": "string", "pattern": MOTIF_DATE},
    "date_declaration": {"type": "string", "pattern": MOTIF_DATE},
    "emirat": {"type": "string", "enum": EMIRATS},
    "montant_dommage_aed": {"type": "number", "minimum": 0},
    "franchise_aed": {"type": "number", "minimum": 0},
    "vetuste": {"type": "number", "minimum": 0, "maximum": 1},
})

SCHEMA_EMBAUCHE = objet({
    "emirates_id": {"type": "string", "pattern": MOTIF_EID},
    "nationalite": {"type": "string", "pattern": "^[A-Z]{2}$"},
    "salaire_base_aed": {"type": "number", "exclusiveMinimum": 0},
    "salaire_total_aed": {"type": "number", "exclusiveMinimum": 0},
    "emirat_travail": {"type": "string", "enum": EMIRATS},
    "zone": {"type": "string", "enum": ["hors_DIFC", "DIFC"]},
    "regime_fin_de_service": {"type": "string", "enum": ["gratuite_33_2021", "pension_nationaux", "epargne_dews"]},
})

SCHEMA_FACTURE = objet({
    "numero_facture": {"type": "string", "pattern": "^FAC-[0-9]{4}-[0-9]{5}$"},
    "montant_ht_aed": {"type": "number", "exclusiveMinimum": 0},
    "tva_aed": {"type": "number", "minimum": 0},
    "ttc_aed": {"type": "number", "exclusiveMinimum": 0},
    "iban": {"type": "string", "pattern": "^AE[0-9]{21}$"},
})


# ---------------------------------------------------------------- règles inter-champs (après le schéma)
def regles_credit(d: dict) -> list[str]:
    erreurs = []
    if d["type_pret"] == "personnel":
        if d["duree_mois"] > 48:
            erreurs.append(f"$.duree_mois : {d['duree_mois']} mois > 48 pour un prêt personnel")
        if d["montant_aed"] > 20 * d["revenu_mensuel_aed"]:
            erreurs.append("$.montant_aed : plus de 20 fois le salaire mensuel pour un prêt personnel")
    m = mensualite(d["montant_aed"], d["taux_annuel"], d["duree_mois"])
    plafond = 0.30 if d["retraite"] else 0.50
    ratio, ok = ratio_endettement(d["mensualites_existantes_aed"], m, d["revenu_mensuel_aed"], plafond)
    if not ok:
        erreurs.append(f"$ : endettement total {ratio:.1%} > plafond {plafond:.0%} (nouvelle mensualité {m:.2f} AED)")
    return erreurs


def regles_estimation(d: dict) -> list[str]:
    erreurs = []
    attendu = d["surface_sqft"] * d["prix_aed_sqft"]
    if abs(d["prix_estime_aed"] - attendu) > 1:
        erreurs.append(f"$.prix_estime_aed : {d['prix_estime_aed']:.0f} ≠ surface × prix au sqft = {attendu:.0f}")
    bas, haut = d["fourchette_aed"]
    if not bas <= d["prix_estime_aed"] <= haut:
        erreurs.append("$.fourchette_aed : l'estimation sort de sa propre fourchette")
    return erreurs


POOLS_AUDITES = {"0x" + "3f" * 20}          # liste blanche de la plateforme (adresse fictive)


def regles_swap(d: dict) -> list[str]:
    erreurs = []
    if d["adresse_pool"].lower() not in POOLS_AUDITES:
        erreurs.append("$.adresse_pool : pool absent de la liste blanche")
    plancher = d["quantite_eth"] * d["prix_reference_aed"] * (1 - d["slippage_max"])
    if abs(d["montant_min_recu_aed"] - plancher) > 0.01:
        cache = 1 - d["montant_min_recu_aed"] / (d["quantite_eth"] * d["prix_reference_aed"])
        erreurs.append(f"$.montant_min_recu_aed : {d['montant_min_recu_aed']:.2f} ≠ {plancher:.2f} "
                       f"(glissement réel {cache:.1%})")
    return erreurs


def regles_sinistre(d: dict) -> list[str]:
    try:
        survenu = date.fromisoformat(d["date_sinistre"])
        declare = date.fromisoformat(d["date_declaration"])
    except ValueError:
        return [f"$ : date inexistante dans le calendrier ({d['date_sinistre']} ou {d['date_declaration']})"]
    if survenu > declare:
        return ["$.date_sinistre : postérieure à la date de déclaration"]
    return []


CODES_ISO_EXTRAIT = {"AE", "EG", "FR", "GB", "IN", "JO", "LB", "PH", "PK"}   # extrait de la liste ISO 3166-1


def regles_embauche(d: dict) -> list[str]:
    erreurs = []
    if not emirates_id_format_valide(d["emirates_id"]):
        erreurs.append("$.emirates_id : format refusé par le contrôle métier")
    if d["nationalite"] not in CODES_ISO_EXTRAIT:
        erreurs.append(f"$.nationalite : {d['nationalite']!r} n'est pas un code ISO 3166-1 alpha-2 attribué")
    if d["salaire_base_aed"] > d["salaire_total_aed"]:
        erreurs.append("$.salaire_base_aed : supérieur au salaire total")
    if d["nationalite"] == "AE":
        attendu = "pension_nationaux"
    elif d["zone"] == "DIFC":
        attendu = "epargne_dews"
    else:
        attendu = "gratuite_33_2021"
    if d["regime_fin_de_service"] != attendu:
        erreurs.append(f"$.regime_fin_de_service : {d['regime_fin_de_service']} au lieu de {attendu}")
    return erreurs


def regles_facture(d: dict) -> list[str]:
    erreurs = []
    if not iban_ae_valide(d["iban"]):
        erreurs.append("$.iban : clé de contrôle mod 97 invalide")
    if abs(d["tva_aed"] - tva(d["montant_ht_aed"])) > 0.01:
        erreurs.append(f"$.tva_aed : {d['tva_aed']:.2f} au lieu de {tva(d['montant_ht_aed']):.2f} (5 %)")
    ecart = abs(d["ttc_aed"] - d["montant_ht_aed"] * 1.05)
    if ecart > 0.01:
        erreurs.append(f"$.ttc_aed : |TTC − HT × 1.05| = {ecart:.2f} AED > 0.01")
    return erreurs


def controler(instance: dict, schema: dict, regles) -> tuple[str, list[str]]:
    """Le schéma d'abord ; les règles métier seulement sur une instance bien formée (sinon elles planteraient)."""
    erreurs = validate(instance, schema)
    if erreurs:
        return "schema", erreurs
    erreurs = regles(instance)
    return ("metier" if erreurs else "ok"), erreurs


def essayer(titre: str, instance: dict, schema: dict, regles, attendu: str) -> list[str]:
    verdict, erreurs = controler(instance, schema, regles)
    print(f"  {titre:<34} → {verdict:<6} {erreurs[0] if erreurs else ''}".rstrip())
    assert verdict == attendu, (titre, verdict, erreurs)
    return erreurs


def main() -> None:
    print("1. Banque — crédit")
    hypo = {"type_pret": "hypothecaire", "montant_aed": 1_000_000, "taux_annuel": 0.045, "duree_mois": 300,
            "revenu_mensuel_aed": 40_000, "mensualites_existantes_aed": 6_000, "retraite": False}
    m = mensualite(1_000_000, 0.045, 300)
    ratio, ok = ratio_endettement(6_000, m, 40_000)
    print(f"  mensualité = {m:.2f} AED ; endettement total = {ratio:.1%} ≤ 50 % : {ok}")
    assert round(m, 2) == 5558.32 and round(ratio, 3) == 0.289 and ok
    r = 0.045 / 12                                            # démonstration, point 1
    assert r == 0.00375 and round((1 + r) ** 300, 5) == 3.07374 and round((1 + r) ** -300, 5) == 0.32534
    assert abs(sum(m / (1 + r) ** k for k in range(1, 301)) - 1_000_000) < 1e-6   # valeur actuelle = capital
    assert mensualite(120_000, 0.0, 24) == 5_000                                     # taux nul : P / n
    dette_max = 0.50 * 40_000 - m                                                    # point 2
    print(f"  dette existante maximale pour ce prêt = {dette_max:.2f} AED")
    assert round(dette_max, 2) == 14_441.68
    essayer("hypothèque, 6 000 AED existants", hypo, SCHEMA_CREDIT, regles_credit, "ok")
    e = essayer("hypothèque, 15 000 AED existants", dict(hypo, mensualites_existantes_aed=15_000),
                SCHEMA_CREDIT, regles_credit, "metier")
    assert "51.4%" in e[0] and round(m / 40_000, 3) == 0.139          # la nouvelle mensualité seule passerait
    perso = dict(hypo, type_pret="personnel", montant_aed=150_000, duree_mois=36, revenu_mensuel_aed=25_000,
                 mensualites_existantes_aed=3_000)
    essayer("personnel, 36 mois", perso, SCHEMA_CREDIT, regles_credit, "ok")
    essayer("personnel, 60 mois", dict(perso, duree_mois=60), SCHEMA_CREDIT, regles_credit, "metier")
    essayer("personnel, 600 000 AED", dict(perso, montant_aed=600_000, duree_mois=48), SCHEMA_CREDIT,
            regles_credit, "metier")
    retraite = dict(hypo, revenu_mensuel_aed=20_000, mensualites_existantes_aed=1_000, retraite=True)
    e = essayer("retraité, plafond 30 %", retraite, SCHEMA_CREDIT, regles_credit, "metier")
    assert "32.8%" in e[0]
    essayer("durée booléenne", dict(hypo, duree_mois=True), SCHEMA_CREDIT, regles_credit, "schema")
    try:                                                      # point 5 : sans le schéma, la règle plante
        regles_credit(dict(hypo, duree_mois="36"))
    except TypeError:
        pass
    else:
        raise AssertionError("une durée en texte aurait dû faire planter la règle")

    print("2. Immobilier — estimation")
    estim = {"emirat": "Dubai", "quartier": "Dubai Marina", "type_bien": "appartement", "surface_sqft": 1250,
             "prix_aed_sqft": 1920, "prix_estime_aed": 2_400_000, "fourchette_aed": [2_250_000, 2_550_000],
             "nb_comparables": 7}
    essayer("1 250 sqft à 1 920 AED/sqft", estim, SCHEMA_ESTIMATION, regles_estimation, "ok")
    print(f"  frais de transfert DLD (4 %) = {0.04 * estim['prix_estime_aed']:.0f} AED")
    assert 1250 * 1920 == 2_400_000 and 0.04 * 2_400_000 == 96_000
    essayer("émirat « Dubaï » accentué", dict(estim, emirat="Dubaï"), SCHEMA_ESTIMATION, regles_estimation, "schema")
    essayer("surface nulle", dict(estim, surface_sqft=0), SCHEMA_ESTIMATION, regles_estimation, "schema")
    essayer("prix total incohérent", dict(estim, prix_estime_aed=2_600_000), SCHEMA_ESTIMATION,
            regles_estimation, "metier")
    essayer("deux comparables seulement", dict(estim, nb_comparables=2), SCHEMA_ESTIMATION,
            regles_estimation, "schema")

    print("3. Crypto — ordre de swap")
    swap = {"adresse_pool": "0x" + "3F" * 20, "quantite_eth": 2, "prix_reference_aed": 12_000,
            "slippage_max": 0.01, "montant_min_recu_aed": 23_760}
    essayer("2 ETH, glissement 1 %", swap, SCHEMA_SWAP, regles_swap, "ok")
    essayer("glissement 0.5 (voulu 0.005)", dict(swap, slippage_max=0.5), SCHEMA_SWAP, regles_swap, "schema")
    essayer("adresse à 39 caractères hexa", dict(swap, adresse_pool="0x" + "3f" * 19 + "3"), SCHEMA_SWAP,
            regles_swap, "schema")
    e = essayer("minimum reçu 20 000 AED", dict(swap, montant_min_recu_aed=20_000), SCHEMA_SWAP, regles_swap,
                "metier")
    assert "16.7%" in e[0]
    essayer("pool hors liste blanche", dict(swap, adresse_pool="0x" + "ab" * 20), SCHEMA_SWAP, regles_swap,
            "metier")

    print("4. Assurance — déclaration de sinistre")
    sinistre = {"numero_police": "POL-204518", "date_sinistre": "2026-03-12", "date_declaration": "2026-03-14",
                "emirat": "Sharjah", "montant_dommage_aed": 18_000, "franchise_aed": 500, "vetuste": 0.2}
    essayer("sinistre le 12, déclaré le 14", sinistre, SCHEMA_SINISTRE, regles_sinistre, "ok")
    essayer("déclaré avant d'être survenu", dict(sinistre, date_declaration="2026-03-10"), SCHEMA_SINISTRE,
            regles_sinistre, "metier")
    essayer("30 février", dict(sinistre, date_sinistre="2026-02-30"), SCHEMA_SINISTRE, regles_sinistre, "metier")
    essayer("date « 12/03/2026 »", dict(sinistre, date_sinistre="12/03/2026"), SCHEMA_SINISTRE,
            regles_sinistre, "schema")
    essayer("franchise négative", dict(sinistre, franchise_aed=-500), SCHEMA_SINISTRE, regles_sinistre, "schema")

    print("5. RH — embauche")
    embauche = {"emirates_id": "784-1990-1234567-1", "nationalite": "IN", "salaire_base_aed": 10_000,
                "salaire_total_aed": 15_000, "emirat_travail": "Dubai", "zone": "hors_DIFC",
                "regime_fin_de_service": "gratuite_33_2021"}
    essayer("salarié indien, Dubai", embauche, SCHEMA_EMBAUCHE, regles_embauche, "ok")
    essayer("nationalité « UK »", dict(embauche, nationalite="UK"), SCHEMA_EMBAUCHE, regles_embauche, "metier")
    essayer("nationalité « in » en minuscules", dict(embauche, nationalite="in"), SCHEMA_EMBAUCHE,
            regles_embauche, "schema")
    essayer("base > total", dict(embauche, salaire_base_aed=16_000), SCHEMA_EMBAUCHE, regles_embauche, "metier")
    essayer("Émirien au régime de gratuité", dict(embauche, nationalite="AE"), SCHEMA_EMBAUCHE,
            regles_embauche, "metier")
    essayer("DIFC au régime d'épargne", dict(embauche, zone="DIFC", regime_fin_de_service="epargne_dews"),
            SCHEMA_EMBAUCHE, regles_embauche, "ok")
    assert validate("784-1990-1234567-1\n", SCHEMA_EMBAUCHE["properties"]["emirates_id"]) == []   # $ et \n final
    assert not emirates_id_format_valide("784-1990-1234567-1\n")                                 # rattrapé ici

    print("6. BTP — facture de sous-traitant")
    facture = {"numero_facture": "FAC-2026-00417", "montant_ht_aed": 120_000, "tva_aed": 6_000,
               "ttc_aed": 126_000, "iban": "AE070331234567890123456"}
    essayer("HT 120 000, TVA 6 000", facture, SCHEMA_FACTURE, regles_facture, "ok")
    arrondi = {"montant_ht_aed": 12_345.67, "tva_aed": round(tva(12_345.67), 2)}
    arrondi["ttc_aed"] = round(arrondi["montant_ht_aed"] + arrondi["tva_aed"], 2)
    essayer("HT 12345.67, TVA arrondie au fils", dict(facture, **arrondi), SCHEMA_FACTURE, regles_facture, "ok")
    assert arrondi["ttc_aed"] == 12_962.95 and abs(12_962.95 - 12_345.67 * 1.05) < 0.004
    essayer("TTC 126 500", dict(facture, ttc_aed=126_500), SCHEMA_FACTURE, regles_facture, "metier")
    essayer("IBAN avec clé fausse (AE08)", dict(facture, iban="AE080331234567890123456"), SCHEMA_FACTURE,
            regles_facture, "metier")
    essayer("IBAN avec espaces", dict(facture, iban="AE07 0331 2345 6789 0123 456"), SCHEMA_FACTURE,
            regles_facture, "schema")
    ligne_ht = 10_010                                         # point 3, en fils : une ligne de 100,10 AED HT
    tva_ligne = (ligne_ht * 5 + 50) // 100                    # 500,5 fils arrondis à 501 (moitié vers le haut)
    ecart_fils = 40 * (ligne_ht + tva_ligne) - 40 * ligne_ht * 105 / 100
    print(f"  40 lignes à TVA arrondie ligne par ligne : écart = {ecart_fils / 100:.2f} AED (borne 40 × 0.005)")
    assert tva_ligne == 501 and ecart_fils == 20 and ecart_fils / 100 > 0.01

    print("7. Mod 97 : toute erreur sur un chiffre ou toute inversion de deux chiffres voisins est détectée")
    iban = "AE070331234567890123456"
    variantes = [iban[:i] + c + iban[i + 1:] for i in range(2, 23) for c in "0123456789" if c != iban[i]]
    inversions = [iban[:i] + iban[i + 1] + iban[i] + iban[i + 2:] for i in range(2, 22) if iban[i] != iban[i + 1]]
    print(f"  {len(variantes)} substitutions et {len(inversions)} inversions : "
          f"{sum(iban_ae_valide(v) for v in variantes + inversions)} acceptée(s)")
    assert len(variantes) == 189 and not any(iban_ae_valide(v) for v in variantes + inversions)

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Banque — crédit
  mensualité = 5558.32 AED ; endettement total = 28.9% ≤ 50 % : True
  dette existante maximale pour ce prêt = 14441.68 AED
…
  hypothèque, 15 000 AED existants   → metier $ : endettement total 51.4% > plafond 50% (nouvelle mensualité 5558.32 AED)
…
  prix total incohérent              → metier $.prix_estime_aed : 2600000 ≠ surface × prix au sqft = 2400000
…
  minimum reçu 20 000 AED            → metier $.montant_min_recu_aed : 20000.00 ≠ 23760.00 (glissement réel 16.7%)
…
  30 février                         → metier $ : date inexistante dans le calendrier (2026-02-30 ou 2026-03-14)
…
  nationalité « UK »                 → metier $.nationalite : 'UK' n'est pas un code ISO 3166-1 alpha-2 attribué
…
  TTC 126 500                        → metier $.ttc_aed : |TTC − HT × 1.05| = 500.00 AED > 0.01
…
  40 lignes à TVA arrondie ligne par ligne : écart = 0.20 AED (borne 40 × 0.005)
7. Mod 97 : toute erreur sur un chiffre ou toute inversion de deux chiffres voisins est détectée
  189 substitutions et 19 inversions : 0 acceptée(s)
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : un schéma arrête ce qui est mal formé, une règle arrête ce qui est incohérent, et les deux ensemble transforment une sortie de modèle en dossier défendable devant un régulateur.

## Squelette algorithmique

Les six cas de ce fichier suivent la même méthode en trois temps : le schéma vérifie la forme, les règles métier vérifient les relations entre champs (le ratio d'endettement, la TVA, les bornes réglementaires), puis une décision tombe. L'algorithme commun est le suivant.

```text
ALGORITHME ContrôlerUneDemande
ENTRÉES : instance JSON, schéma, liste de règles métier
SORTIE  : (verdict, motifs)

  erreurs ← Valider(instance, schéma)                 (étape 8)
  SI erreurs non vide ALORS RETOURNER (« schéma », erreurs)        (les règles planteraient)
  motifs ← RèglesDuCas(instance)                      (liste des règles violées, avec leur chemin)
  SI motifs vide ALORS RETOURNER (« ok », [])
  RETOURNER (« métier », motifs)

ALGORITHME RèglesCrédit (exemple de RèglesDuCas)
  motifs ← liste vide
  SI prêt personnel ET durée > 48 mois ALORS ajouter « durée » à motifs
  SI prêt personnel ET montant > 20 × salaire ALORS ajouter « montant » à motifs
  M ← Mensualité(montant, taux, durée)
  plafond ← 30 % SI retraité SINON 50 %
  SI (mensualités existantes + M) / revenu > plafond ALORS ajouter « endettement » à motifs
  RETOURNER motifs

ALGORITHME Mensualité (règle du cas bancaire)
ENTRÉES : principal P, taux annuel, durée n en mois
SORTIE  : mensualité M

  r ← taux annuel / 12
  SI r = 0 ALORS RETOURNER P / n
  RETOURNER P × r / (1 − (1 + r)^(−n))
```

**Complexité.** La validation est linéaire en la taille de l'instance (étape 8). Chaque règle métier lit un nombre fixe de champs : O(1) par règle, donc O(k) pour k règles. La mensualité coûte O(1) grâce à la formule fermée, alors que la somme actualisée Σ M / (1 + r)^k de la démonstration coûterait O(n) si on l'additionnait terme à terme. La mémoire est celle de l'instance.

**Du squelette au code.** `ContrôlerUneDemande` correspond à `controler`, qui appelle `validate` puis, seulement si l'instance est bien formée, la fonction de règles du cas : `regles_credit`, `regles_estimation`, `regles_swap`, `regles_sinistre`, `regles_embauche` ou `regles_facture`. Elle renvoie l'un des trois statuts « schema », « metier » ou « ok », que `essayer` compare au statut attendu. `RèglesCrédit` correspond à `regles_credit`, qui appelle `mensualite` puis `ratio_endettement` avec un plafond de 30 % pour un retraité et de 50 % sinon. `iban_ae_valide` et `emirates_id_format_valide` sont des règles de format qui complètent le motif du schéma.

## Pièges et limites

- **Une valeur proche n'est pas dans l'énumération.** « Dubaï », « DXB » ou « Abudhabi » sont refusés : on normalise les noms (accents, translittérations, abréviations) avant la validation, en gardant la valeur brute pour l'audit, au lieu d'élargir l'énumération à toutes les variantes rencontrées.
- **Un motif vérifie la forme, pas l'existence.** « UK » respecte `^[A-Z]{2}$`, « 2026-02-30 » respecte le motif de date, et une adresse `0x` de 40 caractères hexadécimaux peut être fausse : la somme de contrôle des adresses (EIP-55) repose sur Keccak-256, qui n'est pas le SHA3-256 de `hashlib` (le remplissage diffère). Chaque identifiant a besoin de son contrôle métier.
- **Les montants en virgule flottante.** `0.1 + 0.2 == 0.3` est faux en Python ; une égalité stricte sur des montants échoue au hasard des arrondis. On compare avec une tolérance justifiée (point 3), ou l'on calcule en fils entiers ou avec `decimal.Decimal`, comme dans l'exemple des 40 lignes.
- **Une tolérance a un domaine de validité.** La règle à 0,01 AED est juste pour une TVA arrondie une fois ; elle refuse à tort une facture arrondie ligne par ligne. Une règle métier doit énoncer l'hypothèse sous laquelle elle est vraie.
- **Les seuils réglementaires changent.** Plafond d'endettement, durée maximale, taux de TVA : on les met en configuration, datés et sourcés, au lieu de les coder en dur, et on les revérifie à chaque changement de texte.

### Exercice feuille blanche

1. Sans regarder le code, écrire `regles_facture` à partir des trois règles du tableau, puis la tester sur HT 120 000 AED, TVA 6 000 AED et TTC 126 000,01 AED. Le verdict attendu est `ok` : l'écart vaut 0,01 AED, égal à la tolérance (en virgule flottante, la différence calculée vaut 0,009999… et passe de justesse).
2. Prédire, puis vérifier : pour l'hypothèque de 1 000 000 AED et un revenu de 40 000 AED, quel verdict avec 14 000 AED de mensualités existantes ? Et avec 14 500 AED ? (Réponses : 48,9 %, `ok` ; 50,1 %, `metier`, puisque Dₘₐₓ = 14 441,68 AED.)
3. Ajouter une règle à `regles_sinistre` : une déclaration tardive de plus de 30 jours (délai illustratif) part en revue humaine. Quel verdict pour un sinistre du 2026-01-02 déclaré le 2026-02-15 ? (Réponse : 44 jours d'écart, donc revue humaine ; `(declare - survenu).days` donne ce nombre.)

## Pour aller plus loin

Les règles inter-champs peuvent aussi s'écrire de façon déclarative, sous forme d'une liste de prédicats nommés (un nom, une fonction, un message), ce qui permet de les journaliser et de les tester une par une ; c'est l'équivalent des contraintes de classe de Bean Validation (`@AssertTrue` sur une méthode, ou un validateur de classe personnalisé). La norme ISO 13616 décrit l'IBAN complet, et la liste officielle des codes ISO 3166-1 se tient à jour : en production, on la charge depuis une source maintenue plutôt qu'en dur.

> Suite : [Les schémas par domaine réglementé](<10-Schemas-Applications-Domaines.md>) — étape 10.
