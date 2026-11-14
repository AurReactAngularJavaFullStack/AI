# Étape 10 — Schémas — Applications par domaine

> Étape 10 du parcours · Prérequis : [Six schémas EAU vérifiés](<09-Schemas-Exemples-Cas-Usage.md>) · Suite : [Taux de validation de schéma](<11-Schemas-Formule-Taux-de-Validation.md>)

**Dossier :** 03-Schemas-Outils-et-Premiere-Evaluation  
**Métiers :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers

L'étape 9 a montré six contrats, un par un. En production, une équipe en exploite plusieurs à la fois, chacun soumis à son régulateur, et elle doit savoir chaque semaine lesquels tiennent leur promesse. Ce fichier donne la vue d'ensemble : un tableau des contrats par domaine, puis un tableau de bord du taux de validation par domaine, avec son intervalle de Wilson et une règle de décision qui ne se laisse pas tromper par un petit échantillon. L'ancienne version de ce fichier tenait en une phrase (« les schémas sont critiques dans tous les domaines réglementés ») : juste, mais sans rien que l'on puisse appliquer.

## Panorama : un contrat par domaine

Les régulateurs sont nommés pour situer la contrainte ; le détail des obligations est à confirmer avec le texte en vigueur.

| Domaine | Schéma (étape 9) | Champs critiques | Règle inter-champs | Contrainte réglementaire |
|---|---|---|---|---|
| Banque | `DemandeCredit` | montant, durée, revenu, mensualités existantes, statut de retraité | endettement total ≤ 50 % (30 % pour un retraité) ; prêt personnel : 48 mois et 20 salaires au plus | CBUAE |
| Immobilier | `Estimation` | émirat, surface en sqft, prix en AED/sqft, fourchette, nombre de comparables | prix estimé = surface × prix au sqft ; estimation dans sa fourchette ; frais de transfert de 4 % affichés à part | DLD/RERA (Ejari pour les baux) |
| Crypto | `OrdreSwap` | adresse du pool, quantité, prix de référence, glissement maximal | minimum reçu = quantité × prix × (1 − glissement) ; pool en liste blanche | VARA |
| Assurance | `DeclarationSinistre` | dates, montants, franchise, vétusté | date existante ; date du sinistre ≤ date de déclaration | CBUAE (supervision de l'assurance) |
| RH | `FicheEmbauche` | Emirates ID, nationalité, salaire de base et total, zone | code ISO 3166-1 attribué ; base ≤ total ; régime de fin de service cohérent avec la nationalité et la zone | MOHRE/WPS |
| BTP | `FactureSousTraitant` | IBAN, HT, TVA, TTC | IBAN mod 97 = 1 ; TVA = 5 % du HT ; écart entre TTC et HT × 1,05 au plus 0,01 AED | autorité fiscale fédérale (TVA) |
| Données personnelles (transverse) | tous les schémas | champs d'identité, de santé, de salaire | `additionalProperties: false` : aucun champ non prévu n'est stocké | PDPL (hors DIFC et ADGM, qui ont leurs propres lois, et hors autorités publiques) |

## Le tableau de bord

### Ce que l'on mesure

Pour chaque domaine et chaque période, on compte les instances reçues, n, et celles qui passent le schéma **et** les règles au premier passage, v, c'est-à-dire sans boucle de réparation. Le taux de validation vaut p̂ = v / n ; il est indéfini (`None`) quand n = 0, parce qu'un domaine sans trafic n'est ni bon ni mauvais. Le tableau suivant sépare les trois objets que l'on confond souvent.

| Fonction de contrôle | Métrique d'évaluation | Seuil |
|---|---|---|
| `validate` puis la fonction de règles du domaine (étape 9) : un verdict par instance | taux de validation au premier passage p̂ = v/n, avec son intervalle de Wilson à 95 % | objectif fixé par domaine (illustratif ici : 0,90 à 0,98), comparé aux **bornes** de l'intervalle, pas au taux seul |

### L'intervalle de Wilson et la règle de décision

Un taux mesuré sur 50 ordres n'a pas la même valeur qu'un taux mesuré sur 3 000 factures. L'intervalle de Wilson donne la plage des taux réels compatibles avec ce que l'on a observé, au niveau de confiance de 95 % (z = 1,96). Sa formule est démontrée à l'[étape 7](<../02-LLM-Softmax-et-Prompts/07-Prompts-Formule-Taux-de-Conformite.md>) ; on l'utilise ici telle quelle, par la fonction canonique `wilson` :

$$
\frac{\hat{p} + \dfrac{z^2}{2n}}{1 + \dfrac{z^2}{n}} \;\pm\; \frac{z}{1 + \dfrac{z^2}{n}}\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}
$$

La règle de décision compare l'objectif τ aux deux bornes [b ; h] de l'intervalle :

- **conforme** si b ≥ τ : même la valeur plausible la plus basse atteint l'objectif ;
- **sous l'objectif** si h < τ : même la valeur plausible la plus haute le manque, et il faut agir ;
- **indéterminé** sinon : l'échantillon ne permet pas de trancher, il faut attendre plus de données avant de conclure dans un sens ou dans l'autre.

## Démonstration

### 1. Le taux global est une moyenne pondérée, et il peut cacher un domaine en échec

Notons

$$
v_d
$$

et

$$
n_d
$$

les comptes du domaine d,

$$
N = \sum_d n_d
$$

et

$$
\hat{p}_d = v_d / n_d .
$$

Le taux global vaut :

$$
\hat{p}_{global} = \frac{\sum_d v_d}{N} = \sum_d \frac{n_d}{N}\,\hat{p}_d
$$

La seconde égalité vient de

$$
v_d = n_d\,\hat{p}_d .
$$

C'est une moyenne des

$$
\hat{p}_d
$$

pondérée par des poids

$$
n_d/N
$$

positifs de somme 1 ; elle est donc comprise entre le plus petit et le plus grand des taux par domaine, parce que

$$
\sum_d \frac{n_d}{N}\hat{p}_d \ge \sum_d \frac{n_d}{N} \min_e \hat{p}_e = \min_e \hat{p}_e ,
$$

et de même pour le maximum. Les gros domaines pèsent le plus : sur la période étudiée, la banque et le BTP représentent 5 000 des 7 450 instances. Le taux global vaut 7 030 / 7 450 = 0,9436, et sa borne basse de Wilson, 0,9382, dépasse 0,90, alors que l'assurance est sous son objectif de 0,90 avec un intervalle [0,8446 ; 0,8942]. Un tableau de bord qui ne montre que le taux global déclarerait tout conforme.

### 2. Pourquoi comparer l'objectif aux bornes, et pas au taux

L'intervalle à 95 % laisse environ 2,5 % de probabilité de chaque côté, à l'approximation de l'intervalle près. Si le taux réel est en dessous de l'objectif, la probabilité que la borne basse dépasse quand même l'objectif est donc d'environ 2,5 % au plus : le verdict « conforme » se trompe rarement. Comparer le taux seul à l'objectif se trompe bien plus souvent. Le RH en donne l'exemple : p̂ = 1 185 / 1 200 = 0,9875 dépasse l'objectif de 0,98, mais la borne basse vaut 0,9795, et le verdict honnête est « indéterminé ». La crypto montre le cas inverse : 45/50 = 0,90 est sous l'objectif de 0,95, mais la borne haute vaut 0,9565 ; avec 50 ordres seulement, on ne peut pas encore affirmer que le contrat est en échec.

### 3. Combien d'instances pour trancher

Pour qu'un intervalle ait une demi-largeur e autour d'un taux voisin de p, il faut environ n = z² p (1−p) / e² instances (formule démontrée à l'étape 7). Avec p = 0,9 et e = 0,02 :

$$
n = 1{,}96^2 \times 0{,}9 \times 0{,}1 / 0{,}02^2 = 864{,}36 ,
$$

soit 865 instances après arrondi à l'entier supérieur. Le programme le vérifie : 778 valides sur 865 donnent un intervalle de demi-largeur 0,0201. Pour la crypto, à 50 ordres par période, il faudrait cumuler 865 / 50 = 17,3, donc 18 périodes avant de trancher à 2 points près.

### 4. Pas de trafic, pas de taux

Avec n = 0, p̂ = 0/0 n'est pas défini : `taux(0, 0)` et `wilson(0, 0)` renvoient `None`, et le verdict est « sans données ». Renvoyer 0 % ferait apparaître en rouge un service qui n'a simplement pas encore servi, et renvoyer 100 % le ferait passer pour parfait ; les deux fausseraient toute moyenne. Inversement, v > n ou v < 0 trahit un bug de comptage : `taux(12, 10)` lève `ValueError` au lieu de renvoyer 1,2.

## Le programme

### Déroulé, ligne par ligne

**`wilson(succes, n, z=1.96)`** est la fonction canonique du parcours, recopiée telle quelle. Pour la crypto, `p = 45 / 50 = 0.9`, `d = 1 + 3.8416 / 50 = 1.076832`, `centre = (0.9 + 3.8416 / 100) / d = 0.87146`, et la demi-largeur vaut 0,08506 : l'intervalle est [0,7864 ; 0,9565]. Elle renvoie `None` pour `n = 0` et lève `ValueError` si `succes` sort de [0 ; n].

**`taille_echantillon(p, demi_largeur)`** applique z² p(1−p)/e² et arrondit au-dessus avec `math.ceil` : `3.8416 * 0.9 * 0.1 / 0.0004 = 864.36`, arrondi à 865.

**`Domaine`** est une `dataclass` qui regroupe, pour une ligne du tableau de bord, le nom du domaine, le nom du schéma, le régulateur, les deux comptes et l'objectif.

**`taux(valides, total)`** renvoie `None` pour un total nul, lève `ValueError` si `valides` sort de [0 ; total], et renvoie le rapport sinon. C'est la convention du parcours : une métrique sans dénominateur est indéfinie, une entrée impossible est une erreur.

**`verdict(valides, total, objectif)`** calcule l'intervalle, puis applique la règle à trois issues : `bas >= objectif` donne « conforme », `haut < objectif` donne « sous l'objectif », le reste « indéterminé ». L'assurance a `haut = 0.8942 < 0.90` : elle est sous l'objectif.

**`DOMAINES`** contient les sept lignes du tableau. Les comptes et les objectifs sont illustratifs ; le secteur public, dont le formulaire vient d'ouvrir, n'a encore reçu aucune instance.

**`main()`**, section par section.

1. La boucle calcule le taux, l'intervalle et le verdict de chaque domaine, et affiche une ligne alignée ; `"—"` remplace les valeurs indéfinies. Les `assert` vérifient les bornes à quatre décimales et les verdicts, puis les deux pièges de la démonstration : le RH dont le taux dépasse l'objectif sans être conforme, la crypto dont le taux le manque sans être en échec.
2. On recalcule le taux global de deux façons, comme rapport des sommes et comme moyenne pondérée, et l'on vérifie qu'elles coïncident, que le résultat est entre le minimum et le maximum des taux, et que sa borne basse dépasse 0,90 alors que l'assurance échoue.
3. `taille_echantillon(0.90, 0.02)` vaut 865 ; l'intervalle obtenu avec 778 valides sur 865 a bien une demi-largeur d'environ 0,02.
4. Deux appels impossibles, `taux(12, 10)` et `taux(-1, 10)`, doivent lever `ValueError`.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`taille_echantillon(p, demi_largeur, z)`** — Cette fonction est l'arpenteur qui dit combien de bornes planter avant de pouvoir mesurer le terrain au mètre près : elle reçoit le taux attendu p, la demi-largeur d'intervalle souhaitée et le quantile z, 1,96 par défaut, lève `ValueError` si p n'est pas strictement entre 0 et 1 ou si la demi-largeur n'est pas positive, puis calcule z² p (1 − p) / e² et arrondit à l'entier supérieur avec `math.ceil`. Elle renvoie ce nombre d'instances : pour un taux de 0,90 et une demi-largeur de 0,02, le calcul donne 864,36, donc 865 instances, et `main` vérifie qu'avec 778 valides sur 865 l'intervalle a bien une demi-largeur d'environ 0,02.

**`taux(valides, total)`** — Celle-ci est le comptable scrupuleux qui refuse de diviser par zéro comme de croire à l'impossible : elle reçoit le nombre d'instances valides et le nombre total reçu sur la période, renvoie `None` quand le total est nul, parce qu'une métrique sans dénominateur est indéfinie et non égale à 0 %, lève `ValueError` si le nombre de valides est négatif ou dépasse le total, et renvoie sinon leur rapport. Pour la banque, 1 840 valides sur 2 000 donnent 0,92 ; le formulaire public, sans aucune instance, reste à `None`, et `taux(12, 10)` comme `taux(-1, 10)` sont refusés.

**`verdict(valides, total, objectif)`** — C'est le juge qui ne tranche que lorsque toute la plage plausible penche du même côté : il reçoit les deux comptes et l'objectif du domaine, calcule l'intervalle de Wilson et renvoie « sans données » s'il n'existe pas, « conforme » si la borne basse atteint l'objectif, « sous l'objectif » si la borne haute reste en dessous, et « indéterminé » dans tous les autres cas. La banque, avec [0,9073 ; 0,9311] face à 0,90, est conforme ; l'assurance, dont la borne haute vaut 0,8942, est sous l'objectif ; et le RH, dont le taux dépasse 0,98 alors que sa borne basse vaut 0,9795, reste indéterminé.

**`main()`** — C'est le responsable qualité qui présente le tableau de bord puis en démonte les pièges : il calcule, pour les sept domaines, le taux, l'intervalle de Wilson et le verdict, imprime une ligne alignée par domaine avec un tiret pour les valeurs indéfinies, et vérifie les bornes à quatre décimales, le domaine public « sans données » et les deux cas trompeurs du RH et de la crypto. Il montre ensuite que le taux global, 7 030 sur 7 450, calculé comme rapport des sommes ou comme moyenne pondérée, dépasse 0,90 alors que l'assurance échoue, puis calcule les 865 instances nécessaires pour trancher à 2 points près et vérifie que deux comptes impossibles lèvent `ValueError`.

```python
"""Étape 10 — tableau de bord du taux de validation par domaine, avec intervalle de Wilson."""
import math
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- statistiques (code canonique, recopié)
def wilson(succes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Intervalle de Wilson à 95 % pour une proportion ; None si n = 0."""
    if n == 0:
        return None
    if not 0 <= succes <= n:
        raise ValueError("il faut 0 <= succes <= n")
    p = succes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - demi, centre + demi)


def taille_echantillon(p: float, demi_largeur: float, z: float = 1.96) -> int:
    """n = z² p (1 − p) / e², arrondi à l'entier supérieur (formule démontrée à l'étape 7)."""
    if not 0 < p < 1 or demi_largeur <= 0:
        raise ValueError("il faut 0 < p < 1 et une demi-largeur > 0")
    return math.ceil(z * z * p * (1 - p) / demi_largeur ** 2)


# ---------------------------------------------------------------- tableau de bord
@dataclass
class Domaine:
    nom: str
    schema: str            # le contrat validé (étape 9)
    regulateur: str        # contrainte réglementaire, nommée seulement
    valides: int           # instances valides au premier passage (schéma + règles)
    total: int             # instances reçues sur la période
    objectif: float        # seuil fixé par l'équipe (illustratif)


def taux(valides: int, total: int) -> float | None:
    """Taux de validation ; None quand il n'y a aucune instance (pas de dénominateur)."""
    if total == 0:
        return None
    if not 0 <= valides <= total:
        raise ValueError("il faut 0 <= valides <= total")
    return valides / total


def verdict(valides: int, total: int, objectif: float) -> str:
    """Conforme si toute la plage plausible est au-dessus de l'objectif ; sous l'objectif si toute est en dessous."""
    intervalle = wilson(valides, total)
    if intervalle is None:
        return "sans données"
    bas, haut = intervalle
    if bas >= objectif:
        return "conforme"
    if haut < objectif:
        return "sous l'objectif"
    return "indéterminé"


DOMAINES = [
    Domaine("Banque", "DemandeCredit", "CBUAE", 1840, 2000, 0.90),
    Domaine("Immobilier", "Estimation", "DLD/RERA", 450, 500, 0.90),
    Domaine("Crypto", "OrdreSwap", "VARA", 45, 50, 0.95),
    Domaine("Assurance", "DeclarationSinistre", "CBUAE", 610, 700, 0.90),
    Domaine("RH", "FicheEmbauche", "MOHRE/WPS, PDPL", 1185, 1200, 0.98),
    Domaine("BTP", "FactureSousTraitant", "autorité fiscale (TVA)", 2900, 3000, 0.95),
    Domaine("Public", "FormulaireBilingue", "règles propres", 0, 0, 0.95),
]


def main() -> None:
    print("1. Tableau de bord du taux de validation au premier passage (période de référence)")
    print(f"  {'domaine':<11}{'schéma':<21}{'valides/total':>14}{'taux':>8}   {'Wilson 95 %':<18}{'objectif':>8}   verdict")
    resultats = {}
    for d in DOMAINES:
        t = taux(d.valides, d.total)
        iv = wilson(d.valides, d.total)
        v = verdict(d.valides, d.total, d.objectif)
        resultats[d.nom] = (t, iv, v)
        t_txt = "—" if t is None else f"{t:.4f}"
        iv_txt = "—" if iv is None else f"[{iv[0]:.4f} ; {iv[1]:.4f}]"
        print(f"  {d.nom:<11}{d.schema:<21}{d.valides:>8}/{d.total:<5}{t_txt:>8}   {iv_txt:<18}{d.objectif:>8.2f}   {v}")

    attendus = {
        "Banque": (0.9073, 0.9311, "conforme"),
        "Immobilier": (0.8706, 0.9233, "indéterminé"),
        "Crypto": (0.7864, 0.9565, "indéterminé"),
        "Assurance": (0.8446, 0.8942, "sous l'objectif"),
        "RH": (0.9795, 0.9924, "indéterminé"),
        "BTP": (0.9596, 0.9725, "conforme"),
    }
    for nom, (bas, haut, v) in attendus.items():
        _, iv, verdict_calcule = resultats[nom]
        assert (round(iv[0], 4), round(iv[1], 4)) == (bas, haut) and verdict_calcule == v, nom
    assert resultats["Public"] == (None, None, "sans données")          # pas de trafic : indéfini, pas 0 %
    assert resultats["RH"][0] > 0.98 and resultats["RH"][2] == "indéterminé"   # le point passe, la borne non
    assert resultats["Crypto"][0] < 0.95 and resultats["Crypto"][2] == "indéterminé"

    print("2. Le taux global masque le domaine en échec")
    avec_trafic = [d for d in DOMAINES if d.total > 0]
    valides = sum(d.valides for d in avec_trafic)
    total = sum(d.total for d in avec_trafic)
    global_ = valides / total
    pondere = sum(d.total / total * (d.valides / d.total) for d in avec_trafic)
    bas, haut = wilson(valides, total)
    print(f"  global = {valides}/{total} = {global_:.4f}, Wilson [{bas:.4f} ; {haut:.4f}] ; Assurance : {resultats['Assurance'][2]}")
    assert valides == 7030 and total == 7450 and abs(global_ - pondere) < 1e-12
    assert min(d.valides / d.total for d in avec_trafic) <= global_ <= max(d.valides / d.total for d in avec_trafic)
    assert bas > 0.90 and resultats["Assurance"][2] == "sous l'objectif"

    print("3. Combien d'instances pour trancher ?")
    n = taille_echantillon(0.90, 0.02)
    print(f"  p = 0.90, demi-largeur 0.02 : n = 1.96² × 0.9 × 0.1 / 0.02² = {n} instances")
    assert n == 865
    bas, haut = wilson(round(0.9 * n), n)
    print(f"  avec {round(0.9 * n)}/{n} valides : Wilson [{bas:.4f} ; {haut:.4f}], demi-largeur {(haut - bas) / 2:.4f}")
    assert abs((haut - bas) / 2 - 0.02) < 0.001

    print("4. Entrées invalides")
    for args in ((12, 10), (-1, 10)):
        try:
            taux(*args)
        except ValueError:
            print(f"  taux{args} → ValueError")
        else:
            raise AssertionError("un nombre de valides hors de [0 ; total] aurait dû être refusé")

    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Tableau de bord du taux de validation au premier passage (période de référence)
  domaine    schéma                valides/total    taux   Wilson 95 %       objectif   verdict
  Banque     DemandeCredit            1840/2000   0.9200   [0.9073 ; 0.9311]     0.90   conforme
  Immobilier Estimation                450/500    0.9000   [0.8706 ; 0.9233]     0.90   indéterminé
  Crypto     OrdreSwap                  45/50     0.9000   [0.7864 ; 0.9565]     0.95   indéterminé
  Assurance  DeclarationSinistre       610/700    0.8714   [0.8446 ; 0.8942]     0.90   sous l'objectif
  RH         FicheEmbauche            1185/1200   0.9875   [0.9795 ; 0.9924]     0.98   indéterminé
  BTP        FactureSousTraitant      2900/3000   0.9667   [0.9596 ; 0.9725]     0.95   conforme
  Public     FormulaireBilingue          0/0           —   —                     0.95   sans données
2. Le taux global masque le domaine en échec
  global = 7030/7450 = 0.9436, Wilson [0.9382 ; 0.9486] ; Assurance : sous l'objectif
3. Combien d'instances pour trancher ?
  p = 0.90, demi-largeur 0.02 : n = 1.96² × 0.9 × 0.1 / 0.02² = 865 instances
  avec 778/865 valides : Wilson [0.8776 ; 0.9177], demi-largeur 0.0201
4. Entrées invalides
  taux(12, 10) → ValueError
  taux(-1, 10) → ValueError
OK — toutes les vérifications sont passées.
```

## Squelette algorithmique

Le tableau de bord de ce fichier transforme des comptes bruts (réponses valides sur réponses totales, par domaine) en une décision justifiée : le taux est-il au-dessus de l'objectif avec une confiance suffisante, et combien de réponses faut-il encore observer pour le savoir ?

```text
ALGORITHME VerdictParDomaine
ENTRÉES : pour chaque domaine d : valides v_d, total n_d ; objectif ; z ; demi-largeur visée h
SORTIE  : pour chaque domaine : taux, intervalle, verdict, taille d'échantillon conseillée

  POUR CHAQUE domaine d FAIRE
      p̂ ← v_d / n_d
      (bas, haut) ← Wilson(v_d, n_d, z)
      SI n_d = 0 ALORS verdict ← « sans données »
      SINON SI bas ≥ objectif ALORS verdict ← « conforme »
      SINON SI haut < objectif ALORS verdict ← « sous l'objectif »
      SINON verdict ← « indéterminé » (mesurer davantage)
      n_conseillé ← ⌈ z² × p̂ × (1 − p̂) / h² ⌉
  FIN POUR
  p̂_global ← Σ v_d / Σ n_d                 (moyenne des p̂_d pondérée par n_d / N)
```

**Complexité.** Chaque domaine coûte O(1) : un quotient, un intervalle de Wilson et une taille d'échantillon. Pour D domaines, le tableau de bord coûte O(D) en temps et en mémoire, quel que soit le nombre de réponses déjà comptées, parce que seuls les compteurs v_d et n_d sont gardés.

**Du squelette au code.** Le taux correspond à `taux`, l'intervalle à `wilson`, la décision à trois issues à `verdict` et la taille d'échantillon à `taille_echantillon`. Le taux global pondéré est calculé dans `main`, qui vérifie qu'il est bien égal à la moyenne des taux par domaine pondérée par leurs volumes.

## Cas d'usage réels aux Émirats

Les volumes, taux et objectifs sont ceux, illustratifs, du tableau de bord ci-dessus ; ils montrent comment lire l'outil, pas l'état d'un marché.

### Banque — un contrat conforme, que l'on surveille quand même

Une banque de détail de Dubaï fait extraire chaque mois environ 2 000 demandes de crédit par son agent, et chaque demande passe par `validate` puis par `regles_credit` (étape 9). Sur la période, 1 840 passent au premier essai : le taux vaut 0,92 et l'intervalle de Wilson [0,9073 ; 0,9311] est tout entier au-dessus de l'objectif de 0,90, d'où le verdict « conforme ». Les 160 échecs ne sont pas tous des défauts du modèle : une partie sont des refus métier légitimes, comme un endettement total au-delà du plafond de 50 % de la CBUAE, et le tableau de bord les ventile par motif pour ne pas mélanger « le modèle lit mal » et « le client n'est pas éligible ». La décision de l'équipe est de ne rien changer au prompt, mais de suivre la borne basse chaque semaine, parce qu'un changement de version du modèle ou de formulaire peut la faire glisser sans prévenir. Sans intervalle, une semaine à 0,915 après une semaine à 0,925 déclencherait une alerte inutile ; avec lui, les deux semaines restent compatibles et l'équipe ne réagit qu'à une vraie dérive (étape 11). L'indicateur publié au comité des risques est la borne basse de Wilson, accompagnée de la part des refus pour endettement.

### Immobilier — un taux à l'objectif, mais rien de prouvé

Une agence de Dubaï et d'Abu Dhabi produit environ 500 estimations par mois avec son agent, et chaque estimation passe par le schéma `Estimation` et la vérification prix = surface × prix au sqft. Le taux vaut exactement 0,90, l'objectif, mais l'intervalle [0,8706 ; 0,9233] le chevauche : le verdict est « indéterminé ». La plupart des échecs viennent de noms d'émirat ou de quartier mal normalisés (« Dubaï », « JVC » pour Jumeirah Village Circle), que le schéma refuse à juste titre. La décision est donc d'ajouter une table de normalisation des noms avant la validation, puis de remesurer, plutôt que de conclure à partir d'un mois de données. Sans tableau de bord, l'équipe aurait célébré un « 90 % » qui pouvait aussi bien cacher un vrai taux de 87 % ; or les estimations publiées doivent rester défendables au regard des règles de la DLD et de la RERA sur l'information des clients. On suit le taux après normalisation et, en aval, l'écart relatif entre estimation et prix de vente enregistré.

### Crypto — trop peu d'ordres pour conclure

Une plateforme agréée par la VARA ne fait passer par son agent qu'environ 50 ordres de swap par semaine, chacun contrôlé par `OrdreSwap` et `regles_swap`. Sur la période, 45 sont valides au premier passage : 0,90, en dessous de l'objectif de 0,95, mais l'intervalle [0,7864 ; 0,9565] contient encore l'objectif, et le verdict est « indéterminé ». Conclure « en échec » sur 50 ordres serait aussi imprudent que conclure « conforme » : la démonstration montre qu'il faudrait environ 865 ordres, soit 18 semaines, pour une précision de 2 points. L'équipe décide donc de cumuler les semaines dans une fenêtre glissante et, en attendant, de garder une revue humaine systématique de chaque ordre refusé. Le garde-fou ne dépend pas de la statistique : un ordre invalide n'est jamais exécuté, quel que soit le taux. La VARA attend que la plateforme sache montrer ses contrôles ; le tableau de bord, avec ses intervalles et ses effectifs, fait partie de cette démonstration. L'indicateur suivi est le nombre d'ordres exécutés hors bornes, qui doit rester à zéro, à côté du taux cumulé.

### Assurance — le seul domaine en échec, invisible dans le taux global

Un assureur auto et santé reçoit environ 700 déclarations de sinistre par période, structurées par l'agent puis contrôlées par `DeclarationSinistre` et `regles_sinistre`. Seules 610 passent au premier essai : 0,8714, avec un intervalle [0,8446 ; 0,8942] entièrement sous l'objectif de 0,90, d'où le verdict « sous l'objectif ». L'analyse des motifs montre que la majorité des échecs sont des dates au format « JJ/MM » recopiées telles quelles depuis la conversation, que le motif `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` refuse. L'équipe corrige le prompt pour demander explicitement le format AAAA-MM-JJ et ajoute une normalisation des dates avant validation, puis remesure sur la période suivante. Sans tableau par domaine, ce défaut serait resté caché : le taux global de 0,9436 et sa borne basse de 0,9382 passent largement l'objectif de 0,90 (démonstration, point 1). L'assurance étant supervisée par la CBUAE, le plan de correction et sa mesure d'efficacité sont consignés. On suit la borne haute de l'intervalle, qui doit repasser au-dessus de 0,90, puis la borne basse.

### RH — au-dessus de l'objectif, mais pas encore conforme

Un cabinet RH multi-émirats traite environ 1 200 fiches d'embauche par période, contrôlées par `FicheEmbauche` et `regles_embauche` avant l'enregistrement auprès du MOHRE et la paie par le WPS. Le taux vaut 0,9875, au-dessus de l'objectif exigeant de 0,98 fixé parce qu'une fiche fausse provoque un rejet de paie ; pourtant, la borne basse vaut 0,9795, et le verdict est « indéterminé ». C'est l'exemple qui justifie la règle de décision : un responsable qui lirait seulement 98,75 % annoncerait un objectif atteint que les données ne prouvent pas encore. Les quinze échecs portent surtout sur des codes de nationalité non attribués (« UK » au lieu de GB) et sur des régimes de fin de service incohérents. La décision est de maintenir la revue humaine des fiches refusées et d'attendre une période de plus, qui devrait suffire à départager. Le schéma joue aussi un rôle de minimisation des données au sens de la PDPL : aucun champ non prévu n'atteint la base. On suit le nombre de rejets de paie WPS imputables à une fiche, objectif zéro, à côté du taux.

### BTP — conforme, et une tolérance à revoir

Un groupe de construction fait lire environ 3 000 factures de sous-traitants par période ; chacune passe par `FactureSousTraitant` et `regles_facture` (IBAN mod 97, TVA de 5 %, écart entre TTC et HT × 1,05). Le taux vaut 0,9667, avec un intervalle [0,9596 ; 0,9725] au-dessus de l'objectif de 0,95 : le verdict est « conforme ». L'analyse des 100 échecs réserve pourtant une surprise : une partie sont des factures justes, émises par des sous-traitants qui arrondissent la TVA ligne par ligne, et que la tolérance de 0,01 AED refuse à tort (étape 9, démonstration, point 3). L'équipe adapte la règle à une tolérance de 0,005 AED par ligne, ce qui fera encore monter le taux, et le conserve comme indicateur de qualité de lecture des PDF. Sans cette analyse, un taux « conforme » aurait caché des retards de paiement injustifiés envers des fournisseurs de bonne foi. La TVA relève de l'autorité fiscale fédérale, et chaque facture bloquée garde son motif pour l'audit. On suit le taux par sous-traitant, qui révèle les modèles de facture mal lus.

### Secteur public — un formulaire sans trafic

Une entité de services publics en ligne, accessible par UAE Pass, vient d'ouvrir un formulaire bilingue rempli par la conversation, contrôlé par le schéma de formulaire bilingue décrit à l'étape 8 (langue, émirat, motif de demande, numéro de mobile). Sur la période, aucune instance n'a encore été reçue : `taux(0, 0)` et `wilson(0, 0)` renvoient `None`, et le tableau affiche « sans données » au lieu d'un 0 % alarmant ou d'un 100 % trompeur. Ce cas n'est pas anecdotique : un tableau qui écrirait 0 % déclencherait une alerte d'astreinte la nuit de l'ouverture, et un tableau qui écrirait 100 % ferait entrer un service non testé dans la moyenne des services conformes. La décision est d'exclure la ligne du taux global tant que n = 0, puis de l'y inclure dès les premières instances. Le régime de protection des données applicable dépend du statut de l'entité, la PDPL excluant les autorités publiques de son champ (à confirmer avec le texte en vigueur) ; la minimisation par `additionalProperties: false` s'applique dans tous les cas. On suivra le taux par langue, arabe et anglais, dès que l'effectif le permettra.

## Pièges et limites

- **Lire le taux sans son effectif.** 0,90 sur 50 instances et 0,90 sur 5 000 ne disent pas la même chose : on publie toujours n et l'intervalle, et l'on décide sur les bornes.
- **Lire le taux global.** C'est une moyenne pondérée par les volumes : les gros domaines y écrasent les petits, et un domaine en échec peut y disparaître. Le tableau se lit ligne par ligne.
- **Confondre refus métier et défaut du modèle.** Un dossier refusé pour endettement excessif est un succès du contrôle, pas un échec de l'extraction ; on ventile les échecs par motif avant d'agir sur le prompt.
- **Changer la règle sans le dire.** Adapter une tolérance ou normaliser des noms fait monter le taux : on date chaque changement de règle pour ne pas le prendre pour une amélioration du modèle.
- **L'indépendance supposée.** L'intervalle de Wilson suppose des instances indépendantes ; cent factures du même sous-traitant, lues avec le même gabarit, échouent ensemble, et l'intervalle est alors trop optimiste. On peut regrouper par fournisseur avant de compter.

### Exercice feuille blanche

1. Sans regarder le code, écrire `verdict(valides, total, objectif)` à partir de `wilson`, puis vérifier les verdicts de la banque (1 840/2 000, objectif 0,90) et de l'assurance (610/700, objectif 0,90).
2. Prédire, puis vérifier : avec 2 × 1 185 = 2 370 valides sur 2 × 1 200 = 2 400, le RH devient-il conforme à l'objectif de 0,98 ? (Indice : le taux ne change pas, l'intervalle se resserre d'un facteur proche de √2. Réponse : oui, l'intervalle devient [0,9822 ; 0,9912], dont la borne basse dépasse 0,98.)
3. Trouver le bug : une variante de `taux` écrit `return valides / total if total else 0.0`. Que devient la ligne du secteur public, et que devient le taux global si l'on y inclut cette ligne avec un poids nul ? Et si une autre variante renvoyait 1,0 ?

> Suite : [Taux de validation de schéma](<11-Schemas-Formule-Taux-de-Validation.md>) — étape 11.
