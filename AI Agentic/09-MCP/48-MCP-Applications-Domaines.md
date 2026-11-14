# Étape 48 — MCP — Applications par domaine

> Étape 48 du parcours · Prérequis : [Exemples MCP de bout en bout](<47-MCP-Exemples-Cas-Usage.md>) · Suite : [Score de disponibilité d'un serveur MCP](<49-MCP-Formule-Score-de-Disponibilite.md>)

**Dossier :** 09-MCP  
**Métiers :** AI Agent Ops, Forward-Deployed Engineers, AI Platform Team

L'ancienne version de ce fichier tenait en une phrase : « MCP est particulièrement utile pour l'intégration chez le client et la plateforme : finance, banque, immobilier, crypto, assurance, RH, BTP. » Elle ne disait ni quels outils exposer, ni quelles données ils touchent, ni quel garde-fou est obligatoire, ni combien coûte ce que l'on expose. Ce fichier donne, pour chacun des sept domaines du parcours, un serveur MCP type : ses outils de lecture et d'écriture, ses resources, la sensibilité de ses données, son garde-fou obligatoire et son objectif de temps de réponse (SLO). Le programme vérifie ces garde-fous avant déploiement, chiffre le coût en contexte des descriptions d'outils, et compare le p95 simulé de chaque serveur à son SLO.

## Lire le tableau

Un outil de **lecture** (L) ne change rien au monde ; un outil d'**écriture** (E) a un effet de bord et passe toujours par une approbation humaine **dans** l'outil, comme `initier_virement` à l'étape 47. La **sensibilité** dit ce que coûterait une fuite : « élevée » pour des données personnelles, financières, de santé ou d'identité, « moyenne » pour des données commerciales. Le **garde-fou obligatoire** est celui sans lequel le serveur ne part pas en production. Le **SLO** est un seuil sur le p95 de la durée d'un `tools/call`, mesurée par le client.

Les SLO, volumes et prix de ce fichier sont illustratifs : ils se fixent avec chaque métier, sur l'historique réel.

## Le tableau par domaine

| Domaine | Serveur | Outils | Resources | Sensibilité | Garde-fou obligatoire | SLO p95 |
|---|---|---|---|---|---|---|
| Banque | `banque-paiements` | L : `solde_compte`, `historique_operations`, `mensualite` ; E : `initier_virement` | barème des frais, conditions du prêt personnel | élevée : financière et personnelle | approbation dans l'outil, plafond par virement, IBAN et Emirates ID masqués | 0,8 s |
| Immobilier | `immo-transactions` | L : `rechercher_biens`, `estimer_prix` ; E : `preparer_contrat_ejari` | comparables par quartier, modèle de contrat Ejari | moyenne : commerciale | relecture humaine du brouillon de contrat, prix calculés par un outil | 1,5 s |
| Crypto | `crypto-surveillance` | L : `carnet_ordres`, `liquidite_pool` | règles d'alerte | élevée : informations de marché | lecture seule ; l'exécution d'ordres vit dans un autre serveur | 0,3 s |
| Assurance | `assurance-sinistres` | L : `statut_sinistre`, `calculer_indemnite` ; E : `declarer_sinistre` | barème des franchises | élevée : santé | données de santé masquées, approbation avant enregistrement | 1,0 s |
| RH | `rh-paie` | L : `contrat_salarie`, `fin_de_service` ; E : `deposer_fichier_wps` | grilles de salaires | élevée : personnelle | approbation, Emirates ID masqué, idempotence par mois | 2,0 s |
| BTP | `btp-facturation` | L : `lire_devis`, `controler_facture` ; E : `emettre_facture` | bordereau de prix unitaires | moyenne : commerciale | idempotence par référence de devis, approbation | 1,5 s |
| Public | `services-publics` | L : `statut_demande` ; E : `deposer_demande` | guides de démarche, en arabe et en anglais | élevée : identité | portée liée à la session UAE Pass, elicitation des champs manquants, masquage | 1,0 s |

Le tableau suivant sépare, pour la latence, la **fonction mesurée** sur chaque appel, la **métrique** calculée sur une fenêtre et le **seuil**. Les valeurs de p95 et de moyenne sont celles de la simulation du programme, sur 400 appels par serveur.

| Domaine | Fonction mesurée par appel | Métrique sur 400 appels | p95 simulé | Moyenne simulée | Seuil (SLO) | Verdict |
|---|---|---|---|---|---|---|
| Banque | durée d'un `tools/call` | p95 au rang le plus proche | 0,601 s | 0,329 s | 0,8 s | respecté |
| Immobilier | idem | idem | 1,072 s | 0,649 s | 1,5 s | respecté |
| Crypto | idem | idem | 0,318 s | 0,165 s | 0,3 s | violé |
| Assurance | idem | idem | 0,811 s | 0,412 s | 1,0 s | respecté |
| RH | idem | idem | 3,029 s | 1,379 s | 2,0 s | violé |
| BTP | idem | idem | 0,794 s | 0,474 s | 1,5 s | respecté |
| Public | idem | idem | 0,776 s | 0,430 s | 1,0 s | respecté |

## Démonstration

### 1. Le coût en contexte des descriptions est additif et linéaire

À chaque appel au modèle, le host renvoie la liste complète des définitions d'outils : nom, description et schéma. Notons tᵢ le nombre de tokens de la définition de l'outil i, N le nombre d'outils exposés à l'agent, R le nombre d'appels au modèle sur la période et π le prix d'un token d'entrée. Le volume de tokens et le coût dus aux seules définitions valent :

$$
T = \sum_{i=1}^{N} t_i
$$

$$
C = R \cdot T \cdot \pi
$$

Le coût est **additif** en outils, parce que T est une somme : retirer un outil retire exactement ses tᵢ tokens de chaque appel. Il est **linéaire** en R et en T : doubler le nombre d'appels ou la taille des descriptions double le coût. R compte des appels au modèle, pas des conversations : une conversation de quatre étapes dans la boucle de l'étape 1 en fait quatre, et 20 000 appels par jour, ce sont par exemple 5 000 conversations de quatre étapes.

Avec les vingt outils du catalogue, le programme mesure T = 1 512 tokens (de 60 à 104 par outil, avec l'approximation de 4 caractères par token de l'étape 4). Sur une journée :

$$
R \cdot T = 20\,000 \times 1\,512 = 30\,240\,000 \text{ tokens}
$$

$$
C = 30{,}24 \times 3 = 90{,}72 \text{ USD par jour}
$$

Le prix de 3 USD par million de tokens est illustratif ; le fournisseur ajoute aussi ses propres tokens de cadrage pour l'utilisation d'outils, que l'approximation ne compte pas.

### 2. Ne donner à l'agent que les outils de son domaine

Si l'agent ne reçoit qu'un sous-ensemble S des outils, le rapport des coûts vaut, par linéarité :

$$
\frac{C_S}{C} = \frac{\sum_{i \in S} t_i}{\sum_{i=1}^{N} t_i}
$$

Si toutes les définitions avaient la même taille, ce rapport vaudrait k/N pour k outils retenus, soit 4/20 = 0,2. Avec les tailles réelles, l'agent bancaire seul coûte 315 / 1 512 = 0,208 fois l'agent branché partout : 18,90 USD au lieu de 90,72 USD par jour. Le gain n'est pas seulement financier. Chaque outil inutile est une occasion de plus, pour le modèle, de choisir le mauvais outil, et une surface de plus pour une injection : un agent bancaire qui ne voit pas `deposer_fichier_wps` ne peut pas être poussé à l'appeler.

### 3. Le cache réduit le prix, pas le volume

Les définitions d'outils font partie du préfixe stable du prompt, que le fournisseur peut mettre en cache (étape 13 ter). Avec le cache, les mêmes T tokens sont **toujours envoyés** à chaque appel ; ils sont seulement facturés à un tarif réduit, noté cπ avec c < 1. Le coût devient :

$$
C_{cache} = R \cdot T \cdot c\,\pi
$$

Avec c = 0,1 (illustratif), on obtient 0,1 × 90,72 = 9,072 USD par jour, ce que le programme vérifie. Le volume, lui, ne baisse pas : les 1 512 tokens occupent toujours la fenêtre de contexte à chaque appel. Le cache et le filtrage des outils se cumulent ; ils ne se remplacent pas. L'écriture initiale du cache est en général facturée plus cher qu'une lecture : le calcul ci-dessus ne compte que les lectures.

### 4. Pourquoi la moyenne passe et le p95 casse

Les durées simulées suivent une loi log-normale : X = exp(μ + σZ), où Z suit la loi normale centrée réduite. C'est la forme typique d'un temps de réponse, toujours positif, avec une queue à droite. Ses quantiles se déduisent de ceux de Z, parce que l'exponentielle est croissante et conserve donc l'ordre :

$$
q_{0{,}95}(X) = e^{\mu + 1{,}645\,\sigma}
$$

Sa moyenne se calcule en complétant le carré dans l'intégrale de la densité normale φ :

$$
\mathbb{E}\left[e^{\sigma Z}\right] = \int_{-\infty}^{+\infty} e^{\sigma z}\,\frac{e^{-z^2/2}}{\sqrt{2\pi}}\,dz = e^{\sigma^2/2}\int_{-\infty}^{+\infty} \frac{e^{-(z-\sigma)^2/2}}{\sqrt{2\pi}}\,dz = e^{\sigma^2/2}
$$

La deuxième égalité vient de σz − z²/2 = σ²/2 − (z − σ)²/2, et la dernière du fait que la densité normale décalée de σ a, elle aussi, une intégrale égale à 1. On en tire la moyenne, puis le rapport entre p95 et moyenne, qui ne dépend que de σ :

$$
\mathbb{E}[X] = e^{\mu + \sigma^2/2}
$$

$$
\frac{q_{0{,}95}(X)}{\mathbb{E}[X]} = e^{1{,}645\,\sigma - \sigma^2/2}
$$

Pour σ = 0,5, ce rapport vaut e⁰,⁶⁹⁷⁵ ≈ 2,01 : le p95 vaut environ **deux fois** la moyenne. Un serveur dont la moyenne est à la moitié du SLO est donc à la limite. C'est le cas du serveur crypto : avec μ = ln 0,15, la théorie donne une moyenne de 0,15 × e⁰,¹²⁵ ≈ 0,170 s et un p95 de 0,15 × e⁰,⁸²² ≈ 0,341 s ; la simulation de 400 appels donne 0,165 s et 0,318 s, et le SLO de 0,3 s est violé. Pour le serveur RH (μ = ln 1,10, σ = 0,6), la théorie donne un p95 de 2,95 s, la simulation 3,029 s, pour un SLO de 2,0 s.

### 5. Le contrôle de catalogue est un refus par défaut

`verifier_catalogue` renvoie la liste des écarts, et le déploiement n'a lieu que si elle est vide. Les règles portent sur ce que le catalogue **déclare** : tout outil d'écriture déclare une approbation, tout montant a son unité dans la description, toute écriture de données sensibles passe par le masquage, tout serveur a un SLO. Ce contrôle ne prouve pas que l'approbation est bien codée dans l'outil : c'est l'invariant de l'étape 47 qui le garantit, et un test qui l'exerce. Il empêche en revanche qu'un serveur parte en production avec un oubli de déclaration, ce que le programme montre deux fois : sur le serveur fautif `crypto-execution`, et sur deux descriptions du catalogue de référence, corrigées après le premier passage du contrôle.

## Le programme

### Déroulé, ligne par ligne

**`p95`** est la fonction canonique du parcours ; **`estimer_tokens`** reprend l'approximation de l'étape 4, `math.ceil(len(texte) / 4)`.

**`OutilMCP`** décrit un outil : nom, description, noms des arguments, et deux drapeaux, `ecriture` et `approbation`. Les fabriques **`L(...)`** et **`E(...)`** créent un outil de lecture, ou d'écriture avec approbation : écrire `E(...)` rend impossible d'oublier le drapeau d'approbation sur un outil d'écriture du catalogue de référence.

**`ServeurDomaine`** décrit un serveur : domaine, nom, outils, resources, sensibilité, masquage, SLO sur le p95 et paramètres `(mu, sigma)` de la latence simulée. **`CATALOGUE`** contient les sept serveurs du tableau, soit 20 outils dont 6 d'écriture.

**`definition_api(o)`** fabrique ce que le modèle reçoit pour chaque outil : `name`, `description` et un `input_schema` strict, où les arguments dont le nom finit par `_aed`, `_sqft` ou désigne un taux deviennent des nombres et les autres des chaînes. **`tokens_outils(outils)`** sérialise chaque définition en JSON, estime ses tokens et additionne : 1 512 pour les vingt outils, 315 pour les quatre outils bancaires.

**`cout_jour_usd(tokens_par_appel, appels_par_jour, prix)`** calcule R × T × π / 10⁶ : 20 000 × 1 512 × 3 / 10⁶ = 90,72 USD.

**`verifier_catalogue(catalogue)`** parcourt chaque serveur et chaque outil et collecte les écarts : écriture sans approbation, argument en AED sans « AED » dans la description, données sensibles écrites sans masquage, SLO absent ou supérieur à 5 s.

**`main()`**, section par section.

1. Affiche le catalogue et vérifie 7 serveurs, 20 outils et 6 outils d'écriture, tous approuvés.
2. Le catalogue de référence ne produit aucun écart. Un catalogue fautif, qui ajoute `crypto-execution` avec `passer_ordre` construit à la main sans approbation, en produit exactement trois.
3. Calcule T, le volume journalier et le coût, pour l'agent branché partout, pour l'agent bancaire seul et avec le cache, puis vérifie l'additivité (T est la somme des tᵢ) et la linéarité (doubler T double le coût).
4. Pour chaque serveur, tire 400 durées log-normales avec un générateur à graine fixe (`random.Random(4800 + i)`), calcule le p95, la moyenne et le verdict. Les `assert` vérifient que le p95 est bien la 380e valeur triée (rang ⌈0,95 × 400⌉ = 380), qu'au moins 380 durées sont inférieures ou égales, et que seuls Crypto (0,318 s) et RH (3,029 s) violent leur SLO.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p95(valeurs)`** — C'est la fonction canonique du parcours, le statisticien qui regarde ce que vivent 95 % des utilisateurs plutôt que la moyenne : elle reçoit une liste de durées, lève une `ValueError` si elle est vide, la trie et renvoie la valeur de rang ⌈0,95 N⌉, toujours une durée réellement observée. Avec 400 appels simulés par serveur, ce rang vaut 380, ce que `main` vérifie pour chacun des sept serveurs ; elle donne 0,318 seconde pour le serveur crypto, au-dessus de son SLO de 0,3 seconde, et 3,029 secondes pour le serveur RH, au-dessus de 2,0 secondes.

**`estimer_tokens(texte)`** — Cette petite fonction est le métreur qui donne un ordre de grandeur sans sortir le mètre-ruban : elle reçoit un texte, divise son nombre de caractères par 4 et arrondit à l'entier supérieur, l'approximation de l'étape 4 pour un texte courant. Elle renvoie ce nombre de tokens estimé ; `tokens_outils` l'applique à la définition JSON de chaque outil, ce qui donne de 60 à 104 tokens par outil et 1 512 tokens pour les vingt outils du catalogue.

**`cout_jour_usd(tokens_par_appel, appels_par_jour, prix_usd_par_million)`** — C'est le comptable qui chiffre la facture quotidienne des descriptions d'outils, renvoyées au modèle à chaque appel : la fonction reçoit le nombre T de tokens de définitions par appel, le nombre R d'appels par jour et le prix π en dollars par million de tokens d'entrée, et renvoie R × T × π / 10⁶. Pour 20 000 appels et 1 512 tokens à 3 USD, elle donne 90,72 USD par jour, 18,90 USD pour l'agent bancaire seul et ses 315 tokens, et 9,072 USD si le préfixe en cache n'est facturé qu'à 10 % ; `main` vérifie aussi que doubler T double le coût.

**`verifier_catalogue(catalogue)`** — Cette fonction est le contrôleur qui refuse par défaut tout déploiement tant que le dossier n'est pas complet : elle reçoit une suite de serveurs et, pour chaque outil, note un écart si un outil d'écriture n'a pas d'approbation humaine ou si un argument en dirhams n'est pas annoncé par « AED » dans la description ; pour chaque serveur, elle en note un si des données sensibles sont écrites sans masquage ou si le SLO est absent ou supérieur à 5 secondes. Elle renvoie la liste des écarts, vide pour le catalogue de référence, et exactement trois écarts pour le catalogue fautif qui ajoute `crypto-execution` et son outil `passer_ordre`.

**`main()`** — Le chef d'orchestre déroule les quatre sections du chapitre : il affiche le catalogue et vérifie 7 serveurs, 20 outils et 6 outils d'écriture, tous approuvés, puis confronte le catalogue de référence, sans écart, au catalogue fautif et à ses trois écarts. Il calcule ensuite le coût en contexte des descriptions, 1 512 tokens et 90,72 USD par jour pour l'agent branché partout, avec l'additivité et la linéarité du coût, et tire enfin 400 durées log-normales par serveur avec une graine fixe pour constater que seuls Crypto et RH violent leur SLO ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 48 — MCP par domaine aux Émirats : catalogue, garde-fous obligatoires, coût des descriptions, p95 contre SLO."""
import json
import math
import random
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- fonctions reprises du parcours
def p95(valeurs: list[float]) -> float:
    """Percentile 95 au rang le plus proche : la valeur de rang ceil(0,95 × N) dans la liste triée."""
    if not valeurs:
        raise ValueError("liste vide")
    s = sorted(valeurs)
    return s[math.ceil(0.95 * len(s)) - 1]


def estimer_tokens(texte: str) -> int:
    """Étape 4 : ordre de grandeur seulement, environ 4 caractères par token pour un texte courant."""
    return math.ceil(len(texte) / 4)


# ---------------------------------------------------------------- le catalogue : un serveur MCP par domaine
@dataclass(frozen=True)
class OutilMCP:
    nom: str
    description: str
    champs: tuple                  # noms des arguments, tous de type texte ou nombre
    ecriture: bool = False
    approbation: bool = False      # approbation humaine DANS l'outil (étape 47)


@dataclass(frozen=True)
class ServeurDomaine:
    domaine: str
    serveur: str
    outils: tuple
    resources: tuple
    sensibilite: str               # "moyenne" ou "élevée"
    masquage: bool                 # données personnelles masquées avant journal et modèle (étape 66)
    slo_p95_s: float
    latence: tuple                 # (mu, sigma) d'une loi log-normale simulée, en secondes


def L(nom: str, description: str, *champs: str) -> OutilMCP:
    return OutilMCP(nom, description, champs)


def E(nom: str, description: str, *champs: str) -> OutilMCP:
    return OutilMCP(nom, description, champs, ecriture=True, approbation=True)


CATALOGUE = (
    ServeurDomaine("Banque", "banque-paiements",
                   (L("solde_compte", "Solde d'un compte identifié par son IBAN émirien, en AED. Lecture seule.", "iban"),
                    L("historique_operations", "Opérations des 90 derniers jours d'un compte, montants en AED. Lecture seule.", "iban"),
                    L("mensualite", "Mensualité d'un prêt amortissable, en AED. Lecture seule.", "principal", "taux_annuel", "n_mois"),
                    E("initier_virement", "Initie un virement en AED après approbation humaine. Écriture.",
                      "iban_source", "iban_beneficiaire", "montant_aed", "reference")),
                   ("banque://baremes/frais-virement", "banque://conditions/pret-personnel"),
                   "élevée", True, 0.8, (math.log(0.30), 0.45)),
    ServeurDomaine("Immobilier", "immo-transactions",
                   (L("rechercher_biens", "Biens à vendre ou à louer par quartier, surface en sqft, prix en AED. Lecture seule.", "quartier", "budget_aed"),
                    L("estimer_prix", "Prix estimé d'un bien à partir de comparables, en AED et AED/sqft. Lecture seule.", "quartier", "surface_sqft"),
                    E("preparer_contrat_ejari", "Prépare un brouillon de contrat de location, loyer en AED, à faire relire. Écriture.",
                      "bien", "locataire", "loyer_annuel_aed")),
                   ("immo://comparables/{quartier}", "immo://modeles/ejari"),
                   "moyenne", True, 1.5, (math.log(0.60), 0.40)),
    ServeurDomaine("Crypto", "crypto-surveillance",
                   (L("carnet_ordres", "Meilleures offres et demandes d'une paire, profondeur en AED. Lecture seule.", "paire"),
                    L("liquidite_pool", "Liquidité et variation sur une heure d'un pool. Lecture seule.", "pool")),
                   ("crypto://regles/alertes",),
                   "élevée", False, 0.3, (math.log(0.15), 0.50)),
    ServeurDomaine("Assurance", "assurance-sinistres",
                   (L("statut_sinistre", "Statut et montant évalué d'un sinistre, en AED. Lecture seule.", "numero"),
                    L("calculer_indemnite", "Indemnité après vétusté, franchise et plafond, en AED. Lecture seule.",
                      "dommage_aed", "vetuste", "franchise_aed", "plafond_aed"),
                    E("declarer_sinistre", "Enregistre une déclaration de sinistre après validation. Écriture.",
                      "police", "date", "description")),
                   ("assur://baremes/franchises",),
                   "élevée", True, 1.0, (math.log(0.35), 0.55)),
    ServeurDomaine("RH", "rh-paie",
                   (L("contrat_salarie", "Contrat et salaire de base d'un salarié, en AED. Lecture seule.", "matricule"),
                    L("fin_de_service", "Indemnité de fin de service (décret-loi fédéral 33/2021), en AED. Lecture seule.",
                      "salaire_base_aed", "annees"),
                    E("deposer_fichier_wps", "Dépose le fichier de salaires du mois après approbation. Écriture.", "mois", "employeur")),
                   ("rh://grilles/salaires",),
                   "élevée", True, 2.0, (math.log(1.10), 0.60)),
    ServeurDomaine("BTP", "btp-facturation",
                   (L("lire_devis", "Lignes d'un devis accepté, montants HT en AED. Lecture seule.", "reference"),
                    L("controler_facture", "Recalcule la TVA de 5 % et la retenue de garantie d'une facture. Lecture seule.", "facture"),
                    E("emettre_facture", "Émet une facture de situation en AED (TVA 5 %), idempotente par référence de devis. Écriture.",
                      "reference_devis", "montant_ht_aed")),
                   ("btp://bordereaux/prix-unitaires",),
                   "moyenne", False, 1.5, (math.log(0.45), 0.35)),
    ServeurDomaine("Public", "services-publics",
                   (L("statut_demande", "Statut d'une démarche de l'usager connecté. Lecture seule.", "numero_demande"),
                    E("deposer_demande", "Dépose une démarche au nom de l'usager connecté. Écriture.", "type", "pieces")),
                   ("public://guides/{demarche}",),
                   "élevée", True, 1.0, (math.log(0.40), 0.40)),
)


def definition_api(o: OutilMCP) -> dict:
    """Ce que le modèle reçoit pour chaque outil, à CHAQUE appel : nom, description, schéma."""
    proprietes = {c: {"type": "number" if c.endswith(("_aed", "_sqft", "annees", "n_mois", "taux_annuel", "vetuste", "principal"))
                      else "string"} for c in o.champs}
    return {"name": o.nom, "description": o.description,
            "input_schema": {"type": "object", "properties": proprietes, "required": list(o.champs),
                             "additionalProperties": False}}


def tokens_outils(outils) -> int:
    return sum(estimer_tokens(json.dumps(definition_api(o), ensure_ascii=False)) for o in outils)


def cout_jour_usd(tokens_par_appel: int, appels_par_jour: int, prix_usd_par_million: float) -> float:
    """C = R × T × prix / 10^6 : chaque appel au modèle renvoie toutes les définitions d'outils."""
    return appels_par_jour * tokens_par_appel * prix_usd_par_million / 1_000_000


def verifier_catalogue(catalogue) -> list[str]:
    """Garde-fous obligatoires, vérifiés avant le déploiement (refus par défaut)."""
    ecarts = []
    for s in catalogue:
        for o in s.outils:
            if o.ecriture and not o.approbation:
                ecarts.append(f"{s.serveur}.{o.nom} : outil d'écriture sans approbation humaine")
            if "AED" not in o.description and any(c.endswith("_aed") for c in o.champs):
                ecarts.append(f"{s.serveur}.{o.nom} : montant sans unité dans la description")
        if s.sensibilite == "élevée" and not s.masquage and any(o.ecriture for o in s.outils):
            ecarts.append(f"{s.serveur} : données sensibles écrites sans masquage")
        if not 0 < s.slo_p95_s <= 5:
            ecarts.append(f"{s.serveur} : SLO absent ou irréaliste")
    return ecarts


def main() -> None:
    print("1. Catalogue par domaine (L = lecture, E = écriture avec approbation)")
    for s in CATALOGUE:
        sorte = " ".join(("E:" if o.ecriture else "L:") + o.nom for o in s.outils)
        print(f"  {s.domaine:<10} {s.serveur:<20} {len(s.outils)} outils, {len(s.resources)} resource(s), "
              f"sensibilité {s.sensibilite}, SLO p95 {s.slo_p95_s} s")
    tous = [o for s in CATALOGUE for o in s.outils]
    assert len(CATALOGUE) == 7 and len(tous) == 20
    assert all(o.approbation for o in tous if o.ecriture) and sum(o.ecriture for o in tous) == 6

    print("2. Garde-fous obligatoires vérifiés avant déploiement")
    assert verifier_catalogue(CATALOGUE) == []
    print("  catalogue de référence : aucun écart")
    fautif = CATALOGUE[:1] + (ServeurDomaine("Crypto", "crypto-execution",
                                             (OutilMCP("passer_ordre", "Passe un ordre au marché.", ("paire", "quantite_aed"), ecriture=True),),
                                             (), "élevée", False, 0.3, (math.log(0.1), 0.5)),)
    ecarts = verifier_catalogue(fautif)
    for e in ecarts:
        print(f"  écart : {e}")
    assert ecarts == ["crypto-execution.passer_ordre : outil d'écriture sans approbation humaine",
                      "crypto-execution.passer_ordre : montant sans unité dans la description",
                      "crypto-execution : données sensibles écrites sans masquage"]

    print("3. Coût en contexte des descriptions d'outils (prix illustratif : 3 USD par million de tokens d'entrée)")
    prix, appels = 3.0, 20_000
    t_tous = tokens_outils(tous)
    t_banque = tokens_outils(CATALOGUE[0].outils)
    par_outil = [tokens_outils([o]) for o in tous]
    print(f"  un agent branché sur les 7 serveurs : N = {len(tous)} outils, T = {t_tous} tokens par appel "
          f"(de {min(par_outil)} à {max(par_outil)} par outil)")
    c_tous = cout_jour_usd(t_tous, appels, prix)
    c_banque = cout_jour_usd(t_banque, appels, prix)
    volume = f"{appels * t_tous:,}".replace(",", " ")
    print(f"  {appels} appels par jour : {volume} tokens, soit {c_tous:.2f} USD par jour")
    print(f"  agent bancaire seul (4 outils, {t_banque} tokens) : {c_banque:.2f} USD par jour, "
          f"rapport {t_banque / t_tous:.3f}")
    c_cache = cout_jour_usd(t_tous, appels, prix * 0.1)
    print(f"  les 20 outils en préfixe mis en cache (lecture facturée 10 %, illustratif) : {c_cache:.2f} USD par jour")
    assert (t_tous, t_banque, appels * t_tous) == (1512, 315, 30_240_000)
    assert (round(c_tous, 2), round(c_banque, 2), round(c_cache, 3)) == (90.72, 18.90, 9.072)
    assert t_tous == sum(par_outil)                                  # le coût est additif outil par outil
    assert abs(cout_jour_usd(2 * t_tous, appels, prix) - 2 * c_tous) < 1e-9   # et linéaire en T
    assert abs(c_banque / c_tous - t_banque / t_tous) < 1e-12
    assert abs(c_cache - 0.1 * c_tous) < 1e-9

    print("4. p95 simulé (graine fixe, 400 appels par serveur) contre le SLO")
    verdicts = {}
    for i, s in enumerate(CATALOGUE):
        rng = random.Random(4800 + i)
        mu, sigma = s.latence
        durees = [rng.lognormvariate(mu, sigma) for _ in range(400)]
        v = p95(durees)
        verdicts[s.domaine] = round(v, 3), v <= s.slo_p95_s
        moyenne = sum(durees) / len(durees)
        print(f"  {s.domaine:<10} p95 = {v:.3f} s  moyenne = {moyenne:.3f} s  SLO {s.slo_p95_s} s : "
              f"{'respecté' if verdicts[s.domaine][1] else 'VIOLÉ'}")
        assert v == sorted(durees)[379]                               # rang ceil(0.95 × 400) = 380
        assert sum(1 for d in durees if d <= v) >= 380
    assert [d for d, (_, ok) in verdicts.items() if not ok] == ["Crypto", "RH"]
    assert verdicts["Crypto"][0] == 0.318 and verdicts["RH"][0] == 3.029
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Catalogue par domaine (L = lecture, E = écriture avec approbation)
  Banque     banque-paiements     4 outils, 2 resource(s), sensibilité élevée, SLO p95 0.8 s
…
2. Garde-fous obligatoires vérifiés avant déploiement
  catalogue de référence : aucun écart
  écart : crypto-execution.passer_ordre : outil d'écriture sans approbation humaine
  écart : crypto-execution.passer_ordre : montant sans unité dans la description
  écart : crypto-execution : données sensibles écrites sans masquage
3. Coût en contexte des descriptions d'outils (prix illustratif : 3 USD par million de tokens d'entrée)
  un agent branché sur les 7 serveurs : N = 20 outils, T = 1512 tokens par appel (de 60 à 104 par outil)
  20000 appels par jour : 30 240 000 tokens, soit 90.72 USD par jour
  agent bancaire seul (4 outils, 315 tokens) : 18.90 USD par jour, rapport 0.208
  les 20 outils en préfixe mis en cache (lecture facturée 10 %, illustratif) : 9.07 USD par jour
4. p95 simulé (graine fixe, 400 appels par serveur) contre le SLO
  Banque     p95 = 0.601 s  moyenne = 0.329 s  SLO 0.8 s : respecté
…
  Crypto     p95 = 0.318 s  moyenne = 0.165 s  SLO 0.3 s : VIOLÉ
…
  RH         p95 = 3.029 s  moyenne = 1.379 s  SLO 2.0 s : VIOLÉ
…
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : exposer un domaine en MCP, c'est faire trois choix vérifiables. Quels outils, et lesquels écrivent ; quel garde-fou est obligatoire avant déploiement ; quel SLO, mesuré au p95 et non à la moyenne. Le coût des descriptions se calcule avant le premier appel.

## Squelette algorithmique

Le programme contient trois algorithmes, appliqués à un catalogue de S serveurs : le contrôle des garde-fous déclarés avant déploiement, le calcul du coût en contexte des définitions d'outils, et la comparaison du p95 de chaque serveur à son SLO. Dans les complexités, n_o est le nombre total d'outils, c le nombre moyen d'arguments par outil, ℓ la longueur moyenne d'une description et n le nombre d'appels simulés par serveur.

### Contrôle de catalogue, refus par défaut

Entrée : le catalogue. Sortie : la liste des écarts ; le déploiement n'a lieu que si elle est vide. Idée : chaque règle est un test local sur un outil ou un serveur, et un seul écart suffit à bloquer.

```text
ALGORITHME VerifierCatalogue
ENTRÉES : catalogue, liste de serveurs (outils, sensibilité, masquage, SLO)
SORTIE  : écarts, liste de messages
  écarts ← []
  POUR chaque serveur s DANS catalogue FAIRE
    POUR chaque outil o DE s FAIRE
      SI o écrit ET o n'a pas d'approbation ALORS ajouter "écriture sans approbation" FIN SI
      SI un argument de o est en AED ET "AED" ∉ description(o) ALORS ajouter "montant sans unité" FIN SI
    FIN POUR
    SI sensibilité(s) = élevée ET NON masquage(s) ET s a un outil d'écriture ALORS
      ajouter "données sensibles écrites sans masquage"
    FIN SI
    SI NON (0 < SLO(s) ≤ 5 s) ALORS ajouter "SLO absent ou irréaliste" FIN SI
  FIN POUR
  RETOURNER écarts                          ▷ déployer seulement si écarts = []
```

**Complexité :** O(n_o × (c + ℓ)) en temps, parce que chaque outil est examiné une fois, que la règle d'unité parcourt ses c arguments et cherche « AED » dans sa description de longueur ℓ, et que les règles de serveur ajoutent O(n_o) au total. En mémoire, O(e) pour les e écarts trouvés.

**Du squelette au code :** c'est `verifier_catalogue` ; la première règle est `o.ecriture and not o.approbation`, la deuxième `"AED" not in o.description and any(c.endswith("_aed") for c in o.champs)`, la troisième teste `s.sensibilite`, `s.masquage` et `any(o.ecriture for o in s.outils)`, la dernière `s.slo_p95_s`. La section 2 de `main()` l'applique au catalogue de référence, puis au catalogue fautif.

### Coût en contexte des définitions d'outils

Entrée : les outils exposés à un agent, le nombre d'appels R et le prix π d'un token. Sortie : le volume T par appel et le coût de la période. Idée : sérialiser chaque définition comme le modèle la recevra, estimer ses tokens, additionner, puis multiplier.

```text
ALGORITHME CoutDefinitions
ENTRÉES : outils o₁, …, o_N ; R appels ; prix π par token
SORTIE  : (T, C)
  T ← 0
  POUR i DE 1 À N FAIRE
    d ← JSON({name, description, input_schema} de oᵢ)
    tᵢ ← ⌈|d| / 4⌉                          ▷ approximation de l'étape 4
    T ← T + tᵢ
  FIN POUR
  C ← R × T × π
  RETOURNER (T, C)                          ▷ T = Σ tᵢ : additif ; C linéaire en R et en T
```

**Complexité :** O(Σ |dᵢ|) en temps, c'est-à-dire la taille totale des définitions, parce que chacune est sérialisée puis mesurée une fois ; le produit final est en O(1). En mémoire, O(max |dᵢ|) pour la définition en cours de sérialisation.

**Du squelette au code :** la sérialisation est `definition_api` suivie de `json.dumps`, l'estimation `estimer_tokens`, la somme `tokens_outils`, et le produit `cout_jour_usd(tokens_par_appel, appels_par_jour, prix)`, qui divise par 10⁶ parce que le prix est donné par million de tokens.

### p95 de chaque serveur contre son SLO

Entrée : pour chaque serveur, les paramètres de latence et le SLO. Sortie : le p95, la moyenne et le verdict. Idée : simuler n durées avec une graine fixe par serveur, puis appliquer la fonction canonique `p95`.

```text
ALGORITHME VerdictsSLO
ENTRÉES : serveurs s₁, …, s_S avec (μ, σ, SLO) ; n appels par serveur
SORTIE  : pour chaque serveur, (p95, moyenne, respecté ou violé)
  POUR i DE 1 À S FAIRE
    initialiser un générateur avec la graine 4800 + i
    x ← [ tirage log-normal(μᵢ, σᵢ) POUR j DE 1 À n ]
    v ← P95(x)                               ▷ valeur de rang ⌈0,95 n⌉ = 380 pour n = 400
    m ← (Σ x) / n
    verdict(sᵢ) ← (v ≤ SLO(sᵢ))
  FIN POUR
  RETOURNER les verdicts
```

**Complexité :** O(S × n log n) en temps, parce que chaque serveur tire n durées en O(n) puis les trie en O(n log n) dans `p95` ; O(n) en mémoire, parce qu'une seule liste de durées est conservée à la fois.

**Du squelette au code :** la boucle est celle de la section 4 de `main()` : `random.Random(4800 + i)`, `rng.lognormvariate(mu, sigma)`, `p95(durees)` et `verdicts[s.domaine] = round(v, 3), v <= s.slo_p95_s`. Les `assert` vérifient que le p95 est bien `sorted(durees)[379]`, la 380e valeur.

## Cas d'usage réels aux Émirats

### Banque — quatre outils, dont un seul qui écrit

Une banque de détail de Dubaï expose à son assistant client le serveur `banque-paiements` : trois outils de lecture (solde, historique des 90 derniers jours, mensualité) et un outil d'écriture, `initier_virement`, qui demande l'approbation du client dans l'application avant tout débit et refuse au-delà de 50 000 AED. Les resources (barème des frais, conditions du prêt personnel) sont lues par le host et placées dans le contexte, si bien que l'agent cite les conditions sans appel d'outil. Les quatre définitions d'outils coûtent 315 tokens à chaque appel du modèle ; sur 20 000 appels par jour et au prix illustratif de 3 USD par million de tokens d'entrée, cela fait 18,90 USD par jour, contre 90,72 USD si l'agent recevait les vingt outils des sept domaines. Les IBAN et les numéros d'Emirates ID sont masqués avant d'être journalisés ou renvoyés au modèle (étape 66). Le p95 simulé, 0,601 s, respecte le SLO de 0,8 s. On suit le p95 par outil et le taux de virements refusés à l'approbation.

### Immobilier — un brouillon de contrat qui ne part jamais seul

Une agence et un promoteur de Dubaï et d'Abu Dhabi exposent la recherche de biens et l'estimation de prix en lecture, et un outil `preparer_contrat_ejari` qui produit un **brouillon** de contrat de location, loyer en AED, que l'agent ne peut pas enregistrer lui-même. L'enregistrement Ejari reste une action humaine, après relecture : un document juridique généré n'a pas de valeur tant qu'un professionnel ne l'a pas vérifié. Les comparables par quartier sont une resource, lue une fois par dossier ; le prix estimé et les frais de transfert DLD de 4 % viennent d'outils. Le contrôle de catalogue du programme a d'ailleurs signalé, lors de sa première exécution, que la description de cet outil ne donnait pas l'unité du loyer : elle a été corrigée avant déploiement. Avec un p95 de 1,072 s pour un SLO de 1,5 s, le serveur est dans les clous. On suit la part des brouillons corrigés lors de la relecture.

### Crypto — un SLO violé malgré une moyenne confortable

Une plateforme d'actifs virtuels agréée par la VARA donne à son agent de surveillance deux outils de lecture : carnet d'ordres et liquidité des pools. L'exécution d'ordres n'est pas dans ce serveur ; elle vit dans un autre, avec d'autres identifiants, que cet agent ne voit pas. Le contrôle de catalogue du programme refuse justement un serveur `crypto-execution` qui exposerait `passer_ordre` sans approbation, sans unité et sans masquage. Le SLO est serré, 0,3 s, parce qu'une alerte de liquidité qui arrive tard ne sert à rien. La moyenne simulée, 0,165 s, est près de deux fois sous le seuil, mais le p95 vaut 0,318 s : un appel sur vingt dépasse le SLO, et c'est ce que voient les opérateurs pendant un pic de volatilité (démonstration, point 4). La décision est d'ajouter une instance ou de réduire la fréquence des appels non critiques. On suit le p95 par fenêtre de cinq minutes.

### Assurance — des données de santé qui ne sortent pas du serveur

Un assureur auto et santé, supervisé par la CBUAE, expose le statut des sinistres et le calcul d'indemnité en lecture, et la déclaration de sinistre en écriture. Les dossiers de santé contiennent des diagnostics : l'outil de statut renvoie le statut et le montant, jamais le diagnostic, et tout texte libre passe par le masquage avant d'atteindre le modèle. `calculer_indemnite` applique min(plafond, max(0, dommage × (1 − vétusté) − franchise)) : 13 900 AED pour 18 000 AED de dommage, 20 % de vétusté et 500 AED de franchise. `declarer_sinistre` demande la validation de l'assuré avant d'enregistrer. Le p95 simulé, 0,811 s, respecte le SLO de 1,0 s. Sans masquage, le journal de l'agent deviendrait une copie non maîtrisée de données médicales. On suit le nombre de données de santé détectées dans les journaux, avec un objectif de zéro.

### RH — un serveur de paie qui dépasse son SLO

Un cabinet RH multi-émirats expose les contrats et le calcul de fin de service en lecture, et le dépôt du fichier de salaires WPS en écriture, avec approbation du gestionnaire et idempotence par mois. Le calcul de fin de service suit le décret-loi fédéral 33/2021 du code canonique : 55 000 AED pour 10 000 AED de base et sept ans. Le serveur s'appuie sur un système de paie ancien : sa moyenne simulée est de 1,379 s, mais son p95 atteint 3,029 s, au-dessus du SLO de 2,0 s. La décision n'est pas de relancer plus souvent, ce qui ajouterait de la charge à un système déjà lent, mais de mettre en cache les lectures de contrat, qui changent rarement, et de garder les appels directs pour le dépôt. Sans SLO suivi au p95, l'équipe aurait conclu, sur la moyenne, que tout allait bien. On suit le p95 après la mise en cache et le nombre de dépôts WPS relancés.

### BTP — une facture émise une seule fois

Un groupe de construction qui mène de grands chantiers à Dubaï expose la lecture des devis acceptés, le contrôle des factures fournisseurs (TVA de 5 %, retenue de garantie) et l'émission des factures de situation. `emettre_facture` est idempotent par référence de devis : si un timeout oblige à relancer, la même référence renvoie la même facture au lieu d'en émettre une seconde (étape 12). L'approbation est demandée au conducteur de travaux, qui voit le montant HT, la TVA et le TTC calculés par l'outil : 120 000 AED HT donnent 6 000 AED de TVA. Le bordereau des prix unitaires est une resource, que le host injecte quand l'agent contrôle une facture. Le p95 simulé, 0,794 s, est sous le SLO de 1,5 s. On suit le nombre de doublons détectés au rapprochement comptable.

### Secteur public — des portées liées à l'usager

Une entité de services publics en ligne, accessible par UAE Pass, expose à son assistant bilingue le statut d'une démarche et son dépôt. Le serveur est distant, en Streamable HTTP, et vérifie lui-même que le jeton présenté appartient à l'usager de la session et porte la portée nécessaire : un agent ne peut consulter que les démarches de la personne connectée. Quand un champ manque, le serveur le demande à l'usager par elicitation au lieu de laisser le modèle le deviner, ce qui respecte la minimisation des données de la PDPL. Les guides de démarche sont des resources en arabe et en anglais. Le p95 simulé, 0,776 s, respecte le SLO de 1,0 s. On suit le taux de démarches déposées sans retour pour pièce manquante.

## Pièges et limites

- **Brancher tous les serveurs sur tous les agents.** Le coût des descriptions croît avec chaque outil ajouté (démonstration, point 1) et chaque outil inutile est une surface d'injection de plus. On donne à chaque agent les serveurs de son domaine, et rien d'autre.
- **Croire que le cache rend les descriptions gratuites.** Il réduit le tarif, pas le volume : les tokens occupent toujours la fenêtre de contexte (démonstration, point 3).
- **Fixer un SLO sur la moyenne.** Avec une queue à droite, le p95 peut valoir deux fois la moyenne ou plus ; un SLO lu sur la moyenne est respecté pendant que les utilisateurs attendent.
- **Additionner des p95.** Une requête qui traverse trois serveurs en série n'a pas pour p95 la somme des trois p95 : cette somme n'est pas une garantie en général. On mesure le p95 de bout en bout, sur la durée totale.
- **Prendre le contrôle de catalogue pour une preuve.** Il vérifie des déclarations. Que l'approbation soit réellement codée dans l'outil se vérifie par un test qui l'exerce, comme le scénario 3 de l'étape 47.

### Exercice feuille blanche

1. Sans regarder le code, écrire `tokens_outils` et `cout_jour_usd`, puis recalculer à la main le coût de l'agent RH seul, dont les trois définitions font 63, 81 et 74 tokens. (Réponse : T = 218 tokens, C = 20 000 × 218 × 3 / 10⁶ = 13,08 USD par jour.)
2. Prédire, puis vérifier : si le serveur crypto passe à σ = 0,3 avec la même médiane de 0,15 s, son SLO de 0,3 s est-il respecté en théorie ? (Réponse : le p95 vaut 0,15 × e⁰,⁴⁹³⁵ ≈ 0,246 s, sous le seuil.)
3. Trouver le bug : une variante écrit `if o.ecriture or not o.approbation:` dans `verifier_catalogue`. Que renvoie-t-elle sur le catalogue de référence ? (Réponse : un écart pour chacun des 20 outils : les 6 outils d'écriture, parce que `o.ecriture` suffit à rendre la condition vraie, et les 14 outils de lecture, qui n'ont pas d'approbation et n'en ont pas besoin. La condition correcte est `o.ecriture and not o.approbation`.)

## Pour aller plus loin

La recherche d'outils (tool search) pousse la logique du point 2 plus loin : l'agent ne reçoit qu'un outil de recherche et quelques outils toujours utiles, et charge les autres définitions à la demande. MCP permet aussi au serveur de signaler un changement de liste (`notifications/tools/list_changed`), ce qui invalide le préfixe mis en cache : on évite de faire varier la liste en cours de conversation. Le calcul de la disponibilité d'un serveur, et d'une chaîne de serveurs, est l'objet de l'étape suivante.

> Suite : [Score de disponibilité d'un serveur MCP](<49-MCP-Formule-Score-de-Disponibilite.md>) — étape 49.
