# Étape 40 bis — Orchestration — Définitions fondamentales : faire travailler plusieurs étapes et plusieurs agents

> Étape 40 bis du parcours · Prérequis : [Coût dans A*](<../07-Planification/40-Planification-Formule-A-Star.md>) · Suite : [Score de priorité de tâche](<41-Orchestration-Formule-Score-de-Priorite.md>)

**Dossier :** 08-Orchestration  
**Métiers :** AI Engineers, AI Platform Team, Forward-Deployed Engineers

Orchestrer, c'est décider qui fait quoi, dans quel ordre et en parallèle ou non, quand un travail ne tient pas dans une seule boucle d'agent. Ce fichier distingue workflow et agent, présente les cinq motifs d'orchestration les plus utilisés, puis les questions de production : état partagé, reprise après panne, intervention humaine. Il construit enfin un routeur, un éventail d'ouvriers en parallèle, une boucle évaluateur-optimiseur et une exécution durable qui reprend après un plantage sans refaire ce qui est fait. Les outils mathématiques du dossier suivent : score de priorité (étape 41), graphes et tri topologique (étapes 42 à 45).

## Définitions

### Workflow et agent

Dans un **workflow**, le code fixe l'enchaînement : étape 1, puis 2, puis 3, et le modèle remplit chaque étape. Dans un **agent**, le modèle choisit lui-même la suite (étape 1). Le workflow est prévisible, testable et moins cher ; l'agent s'adapte aux cas imprévus. Règle de conduite : commencer par le plus simple qui marche. Un appel unique bien outillé, puis un workflow, puis un agent, puis plusieurs agents, et chaque marche se justifie par une mesure (étape 13 bis).

### Les cinq motifs

| Motif | Principe | Exemple |
|---|---|---|
| **Chaînage** | la sortie d'un appel est l'entrée du suivant, avec un contrôle entre les deux | extraire une facture → valider le schéma → rédiger l'avis |
| **Routage** | un premier appel classe la demande et l'envoie vers le traitement spécialisé | achat, location ou réclamation |
| **Parallélisation** | des appels indépendants tournent en même temps ; variante *vote* : le même appel plusieurs fois, et l'on agrège | titre, charges et prix d'un bien vérifiés simultanément |
| **Orchestrateur-ouvriers** | un orchestrateur découpe dynamiquement le travail, distribue aux ouvriers et assemble | analyse d'un appel d'offres lot par lot |
| **Évaluateur-optimiseur** | un appel produit, un autre évalue selon des critères, on boucle jusqu'à satisfaction ou limite | rédiger un avis jusqu'à ce qu'il couvre les trois rubriques |

Ces motifs se combinent : un routeur envoie vers un orchestrateur, dont les ouvriers sont des workflows.

### Système multi-agent

Un système multi-agent fait collaborer plusieurs agents, chacun avec son prompt, ses outils et son **propre contexte**. Le **superviseur** répartit le travail et assemble ; le **transfert** (*handoff*) passe la conversation d'un agent à un autre (accueil, puis spécialiste). L'intérêt principal est l'isolation des contextes : un ouvrier lit 200 pages et ne renvoie qu'une fiche, et l'agent principal garde un contexte court (étape 13 ter). Le prix est réel : plus d'appels, plus de tokens au total, et des erreurs qui se propagent d'un agent à l'autre. Les erreurs de plusieurs agents qui partagent le même modèle et les mêmes sources sont corrélées : trois agents ne valent pas trois vérifications indépendantes.

### État partagé et points de reprise

L'orchestrateur tient un **état** : ce qui est fait, ce qui reste, les résultats intermédiaires. Il l'enregistre après chaque étape terminée, dans un **point de reprise** (*checkpoint*) persistant. Après un plantage ou un redéploiement, il recharge le dernier point de reprise et reprend là où il s'était arrêté.

### Exécution durable et idempotence

Une exécution durable garantit qu'un travail long finit, même à travers des pannes. Deux règles la rendent sûre. Une étape terminée et enregistrée n'est jamais refaite. Une étape interrompue au milieu peut être refaite, donc elle doit être **idempotente** : la rejouer avec la même clé d'idempotence ne crée pas un second bon de commande ni un second paiement.

### Intervention humaine

L'orchestration prévoit des **points d'arrêt** où le travail attend une décision humaine : approbation d'un montant, choix entre deux options, relecture d'un avis. L'état est enregistré, le processus peut s'arrêter des heures, et la reprise se fait avec la décision.

## Équations

Pour des étapes représentées par un graphe de dépendances, la latence est celle du **chemin critique**, le coût est la **somme** :

$$
T_{\text{total}} = \max_{\text{chemins } c} \sum_{i \in c} T_i, \qquad C_{\text{total}} = \sum_i C_i + C_{\text{orchestration}}
$$

Pour m ouvriers en parallèle suivis d'une agrégation :

$$
T_{\text{parallèle}} = \max_i T_i + T_{\text{agrégation}}, \qquad T_{\text{séquentiel}} = \sum_i T_i + T_{\text{agrégation}}
$$

Si chaque ouvrier respecte un délai t avec la probabilité q, indépendamment, l'éventail entier le respecte avec la probabilité :

$$
P\left(\max_i T_i \le t\right) = q^m
$$

## Démonstration

**Chemin critique.** Une étape ne commence qu'après toutes celles dont elle dépend. La fin du travail arrive donc à la fin de la chaîne de dépendances la plus longue en durée, et paralléliser ne raccourcit que les chaînes qui ne sont pas critiques. Le coût, lui, se paie pour chaque appel, quel que soit l'ordre : paralléliser ne fait pas économiser un seul token.

**Exemple.** Trois ouvriers de 2, 3 et 4 secondes, puis une agrégation de 1 seconde : en séquence, 2 + 3 + 4 + 1 = 10 s ; en parallèle, max(2, 3, 4) + 1 = 5 s. Le coût est identique dans les deux cas.

**La queue des latences.** maxᵢ Tᵢ ≤ t exige que **chaque** Tᵢ ≤ t ; par indépendance, la probabilité est le produit des q, soit qᵐ. Si chaque ouvrier tient 4 secondes dans 95 % des cas, dix ouvriers en parallèle tiennent tous les 4 secondes dans 0,95¹⁰ = 0,599 des cas seulement : le 95ᵉ centile de l'éventail est bien pire que celui d'un ouvrier. Paralléliser beaucoup d'appels fait remonter la queue ; on borne chaque ouvrier par un délai et on accepte de conclure sans le retardataire quand c'est possible.

## Architecture hexagonale : l'orchestrateur est un service d'application

L'orchestrateur vit dans la couche application : il enchaîne des cas d'usage du domaine et des appels de ports (modèle, outils, magasin d'état). Le magasin de points de reprise est un port (`CheckpointStore`), avec un adaptateur base de données en production et un dictionnaire en test. En Java, ce rôle est souvent tenu par un moteur de workflow durable ; l'important est de savoir ce qu'il garantit : reprise, idempotence, attente d'un humain.

## Construire depuis une feuille blanche

On construit l'orchestration d'une agence immobilière de Dubaï qui prépare un avis d'achat. Un routeur classe la demande ; pour un achat, trois ouvriers vérifient en parallèle le titre de propriété, les charges de copropriété et le prix ; un évaluateur exige que l'avis couvre les trois rubriques et renvoie le brouillon à l'optimiseur sinon. Une seconde partie déroule une chaîne d'étapes avec points de reprise, simule un plantage, reprend, et vérifie qu'aucune étape terminée n'est refaite et que l'étape interrompue, rejouée, ne crée pas de doublon.

### Déroulé, ligne par ligne

**`router(demande)`** classe par mots-clés : `achat`, `location`, sinon `humain`. En production, c'est un appel au modèle avec une sortie structurée (étape 8) et un `enum` de routes ; une demande hors des routes connues va vers un humain, jamais vers une route par défaut.

**`OUVRIERS`** associe chaque vérification à une fonction et à une durée simulée (2, 3 et 4 secondes). `eventail(dossier)` les lance avec `ThreadPoolExecutor` : les appels partent en même temps. La latence affichée est calculée par la formule (`max + agrégation`), pas mesurée à l'horloge, pour que la sortie soit identique à chaque exécution.

**`evaluateur(avis)`** renvoie la liste des rubriques manquantes. **`optimiseur(avis, manquantes, resultats)`** ajoute les rubriques manquantes à partir des résultats des ouvriers. **`boucle_eval_optim`** alterne les deux au plus `max_tours` fois. Le premier brouillon oublie les charges ; le second est complet.

**`Durable`** déroule une chaîne d'étapes. Après chaque étape terminée, il écrit l'état en JSON dans `self.stockage` (le point de reprise). `crash_avant` lève une exception juste avant une étape donnée, pour simuler un plantage. `reprendre()` recharge le JSON et saute les étapes déjà présentes dans `faites`.

**`creer_offre(cle)`** est l'étape à effet de bord : elle enregistre une offre dans `OFFRES`, indexée par sa clé d'idempotence. Rejouée avec la même clé, elle renvoie l'offre existante au lieu d'en créer une seconde.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier_titre(dossier)`** — Ce premier ouvrier joue le clerc de notaire qui consulte le registre foncier : il reçoit la référence du dossier, ajoute 1 à la case `"titre"` du compteur global `APPELS`, puis renvoie une phrase fixe qui annonce une propriété libre, enregistrée et sans hypothèque. La réponse est écrite en dur, car seul compte ici le motif d'orchestration ; le compteur permet à `main` de vérifier que l'éventail a appelé chaque ouvrier exactement une fois, et la phrase, qui commence par `titre :`, permet à `evaluateur` de reconnaître la rubrique dans l'avis.

**`verifier_charges(dossier)`** — Le deuxième ouvrier est le syndic qu'on interroge sur les charges de copropriété : il reçoit la référence du dossier, ajoute 1 à la case `"charges"` du compteur `APPELS`, et renvoie une phrase fixe, des charges de 18 AED par pied carré et par an, sans impayé. Dans `OUVRIERS`, on lui attribue une durée simulée de 3 secondes ; c'est précisément sa rubrique que le premier brouillon oublie, si bien que l'optimiseur doit aller chercher sa phrase dans les résultats de l'éventail pour compléter l'avis.

**`estimer_prix(dossier)`** — Le troisième ouvrier est l'expert qui compare le bien aux ventes voisines : il reçoit la référence du dossier, ajoute 1 à la case `"prix"` du compteur, et renvoie une phrase fixe qui situe le prix à 2,2 millions de dirhams, dans la fourchette des comparables. C'est l'ouvrier le plus lent, avec une durée simulée de 4 secondes, et c'est donc lui qui fixe la latence de l'éventail parallèle, 4 + 1 = 5 secondes, agrégation comprise.

**`eventail(dossier)`** — C'est le chef d'équipe qui envoie ses trois ouvriers sur le terrain en même temps au lieu de les faire passer l'un après l'autre : la fonction reçoit la référence du dossier, ouvre un `ThreadPoolExecutor` d'autant de fils que d'ouvriers, soumet chaque vérification d'un coup, puis attend et range chaque résultat sous son nom. Elle renvoie le dictionnaire des trois résultats, la latence parallèle calculée par la formule, le maximum des durées plus l'agrégation, soit 5 secondes, et la latence séquentielle, leur somme plus l'agrégation, soit 10 secondes ; ces durées sont calculées, non mesurées, pour que la sortie soit toujours identique.

**`evaluateur(avis)`** — Cette fonction est le relecteur exigeant qui coche, sur une liste de contrôle, les trois rubriques obligatoires : elle reçoit le texte de l'avis et renvoie, dans l'ordre titre, charges, prix, la liste des rubriques dont l'étiquette suivie d'un deux-points n'apparaît nulle part dans le texte. Une liste vide signifie que l'avis est complet ; sur le premier brouillon, elle renvoie `['charges']`, et sur l'avis final une liste vide, ce que `main` vérifie avant d'accepter le résultat de la boucle.

**`optimiseur(avis, manquantes, resultats)`** — C'est le rédacteur qui reprend la copie renvoyée par le relecteur : il reçoit l'avis, la liste des rubriques manquantes et les résultats des ouvriers, puis ajoute à la fin de l'avis, pour chaque rubrique manquante, une nouvelle ligne à puce qui recopie la phrase de l'ouvrier correspondant. Il renvoie l'avis ainsi complété, sans toucher aux lignes déjà présentes ; dans un vrai système, ce serait un nouvel appel au modèle avec les remarques de l'évaluateur, mais le principe de la boucle reste le même.

**`boucle_eval_optim(brouillon, resultats, max_tours)`** — Cette fonction organise l'aller-retour entre le relecteur et le rédacteur, avec une limite pour ne jamais tourner sans fin : elle reçoit le brouillon, les résultats des ouvriers et un nombre maximal de 3 tours par défaut, et, à chaque tour, demande à `evaluateur` ce qui manque, renvoie l'avis avec le numéro du tour si rien ne manque, et sinon le fait compléter par `optimiseur`. Elle renvoie le couple formé de l'avis et du numéro du tour où il a été jugé complet, 2 dans l'exemple, ou, si le budget s'épuise, le dernier avis avec `max_tours`.

**`creer_offre(cle)`** — C'est le guichet qui émet les offres d'achat et qui tient un registre pour ne jamais en émettre deux pour la même demande : la fonction reçoit une clé d'idempotence, ajoute 1 à la case `"creer_offre"` du compteur, puis, si la clé n'est pas encore dans `OFFRES`, y enregistre un nouveau numéro formé sur le nombre d'offres existantes, `OFFRE-001` pour la première. Elle renvoie le numéro associé à la clé, ancien ou nouveau ; `main` vérifie que l'étape n'a été exécutée qu'une fois malgré le plantage, puis qu'un rappel avec la même clé rend toujours `OFFRE-001` sans créer de doublon.

**`Durable.__init__(etapes)`** — Le constructeur prépare le registre de bord d'un convoi qui doit pouvoir repartir après une panne : il reçoit la liste ordonnée des étapes, chacune formée d'un nom et d'une fonction qui reçoit l'état, la range dans l'objet et initialise à `None` le stockage du point de reprise. Il ne renvoie rien ; dans `main`, le convoi compte quatre étapes, vérifier, rédiger, créer l'offre et notifier, et le stockage n'est qu'une chaîne JSON en mémoire, là où la production utiliserait un adaptateur de base de données derrière le port `CheckpointStore`.

**`Durable.executer(etat, crash_avant)`** — Cette méthode est le chef de convoi qui avance d'étape en étape en notant chaque progrès dans le registre : elle reçoit l'état, un dictionnaire qui contient notamment les étapes déjà faites, et facultativement le nom d'une étape avant laquelle simuler un plantage, puis saute chaque étape déjà enregistrée, lève l'exception `Plantage` si elle arrive à l'étape désignée, et sinon exécute l'étape, range son résultat dans l'état et écrit l'état complet en JSON dans le stockage. Elle renvoie l'état final ; dans `main`, le plantage avant « notifier » laisse un point de reprise qui contient déjà les trois premières étapes.

**`Durable.reprendre()`** — Cette méthode est le redémarrage du convoi après la panne : elle ne reçoit rien, relit dans le stockage la chaîne JSON du dernier point de reprise, la transforme en dictionnaire et la passe à `executer`, cette fois sans plantage simulé. Comme `executer` saute toutes les étapes déjà enregistrées, seule l'étape « notifier » est jouée ; la méthode renvoie l'état final avec les quatre étapes dans l'ordre, et `main` vérifie que `creer_offre` n'a été appelée qu'une seule fois au total.

**`main()`** — Le chef d'orchestre déroule les cinq tableaux de l'agence : il fait classer trois demandes par `router`, en achat, location et humain, lance l'éventail parallèle et vérifie les latences de 5 et 10 secondes ainsi qu'un appel par ouvrier, puis fait compléter par la boucle évaluateur-optimiseur un brouillon qui oublie les charges. Il simule ensuite un plantage dans l'exécution durable, reprend, et vérifie qu'aucune étape n'a été refaite ni dupliquée, avant de calculer la queue des latences, 0,95¹⁰ = 0,599 ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 40 bis — orchestration : routage, éventail parallèle, évaluateur-optimiseur, exécution durable."""
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

APPELS = Counter()


def router(demande: str) -> str:
    d = demande.lower()
    if "acheter" in d or "achat" in d:
        return "achat"
    if "louer" in d or "location" in d:
        return "location"
    return "humain"


def verifier_titre(dossier):
    APPELS["titre"] += 1
    return "titre : propriété libre, enregistrée au DLD, sans hypothèque"


def verifier_charges(dossier):
    APPELS["charges"] += 1
    return "charges : 18 AED/sqft/an, aucun impayé"


def estimer_prix(dossier):
    APPELS["prix"] += 1
    return "prix : 2,2 M AED, dans la fourchette des comparables"


OUVRIERS = {"titre": (verifier_titre, 2.0), "charges": (verifier_charges, 3.0), "prix": (estimer_prix, 4.0)}
T_AGREGATION = 1.0


def eventail(dossier: str) -> tuple[dict, float, float]:
    with ThreadPoolExecutor(max_workers=len(OUVRIERS)) as ex:
        futurs = {nom: ex.submit(f, dossier) for nom, (f, _) in OUVRIERS.items()}
        resultats = {nom: fut.result() for nom, fut in futurs.items()}
    durees = [d for _, d in OUVRIERS.values()]
    return resultats, max(durees) + T_AGREGATION, sum(durees) + T_AGREGATION


def evaluateur(avis: str) -> list[str]:
    return [r for r in ("titre", "charges", "prix") if f"{r} :" not in avis]


def optimiseur(avis: str, manquantes: list[str], resultats: dict) -> str:
    return avis + "".join(f"\n- {resultats[r]}" for r in manquantes)


def boucle_eval_optim(brouillon: str, resultats: dict, max_tours: int = 3) -> tuple[str, int]:
    avis = brouillon
    for tour in range(1, max_tours + 1):
        manquantes = evaluateur(avis)
        if not manquantes:
            return avis, tour
        avis = optimiseur(avis, manquantes, resultats)
    return avis, max_tours


OFFRES = {}


def creer_offre(cle: str) -> str:
    """Étape à effet de bord, idempotente : la même clé ne crée jamais deux offres."""
    APPELS["creer_offre"] += 1
    if cle not in OFFRES:
        OFFRES[cle] = f"OFFRE-{len(OFFRES) + 1:03d}"
    return OFFRES[cle]


class Plantage(Exception):
    pass


class Durable:
    def __init__(self, etapes: list[tuple[str, callable]]):
        self.etapes, self.stockage = etapes, None

    def executer(self, etat: dict, crash_avant: str | None = None) -> dict:
        for nom, f in self.etapes:
            if nom in etat["faites"]:
                continue                                   # déjà fait et enregistré : on saute
            if nom == crash_avant:
                raise Plantage(f"plantage avant {nom}")
            etat["faites"][nom] = f(etat)
            self.stockage = json.dumps(etat, ensure_ascii=False)   # point de reprise
        return etat

    def reprendre(self) -> dict:
        return self.executer(json.loads(self.stockage))


def main() -> None:
    print("1. Routage")
    routes = {d: router(d) for d in ("Je veux acheter un 2 chambres à Marina", "Location à JVC ?", "Mon voisin fait du bruit")}
    for d, r in routes.items():
        print(f"  {d!r:<45} -> {r}")
    assert list(routes.values()) == ["achat", "location", "humain"]

    print("2. Éventail parallèle")
    resultats, t_par, t_seq = eventail("Marina Gate, appt 1204")
    print(f"  {len(resultats)} vérifications ; latence parallèle {t_par:.0f} s, séquentielle {t_seq:.0f} s")
    assert (t_par, t_seq) == (5.0, 10.0) and APPELS == Counter(titre=1, charges=1, prix=1)

    print("3. Évaluateur-optimiseur")
    brouillon = f"Avis d'achat — Marina Gate 1204\n- {resultats['titre']}\n- {resultats['prix']}"
    print(f"  manquant au 1er tour : {evaluateur(brouillon)}")
    avis, tours = boucle_eval_optim(brouillon, resultats)
    print(f"  avis complet au tour {tours}")
    assert evaluateur(brouillon) == ["charges"] and evaluateur(avis) == [] and tours == 2

    print("4. Exécution durable")
    flux = Durable([
        ("verifier", lambda e: "vérifications faites"),
        ("rediger", lambda e: "avis rédigé"),
        ("creer_offre", lambda e: creer_offre(f"{e['dossier']}:offre")),
        ("notifier", lambda e: "client notifié"),
    ])
    etat = {"dossier": "MG-1204", "faites": {}}
    try:
        flux.executer(etat, crash_avant="notifier")
    except Plantage as p:
        print(f"  {p} ; point de reprise : {sorted(json.loads(flux.stockage)['faites'])}")
    final = flux.reprendre()
    print(f"  reprise : {list(final['faites'])} ; offre {final['faites']['creer_offre']}")
    assert list(final["faites"]) == ["verifier", "rediger", "creer_offre", "notifier"]
    assert APPELS["creer_offre"] == 1                         # l'étape terminée n'a pas été refaite
    assert creer_offre("MG-1204:offre") == "OFFRE-001" and len(OFFRES) == 1   # rejouée : pas de doublon

    print("5. Queue des latences")
    for m in (1, 3, 10):
        print(f"  {m:>2} ouvriers à 95 % sous 4 s : tous sous 4 s dans {0.95 ** m:.3f} des cas")
    assert round(0.95 ** 10, 3) == 0.599
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Routage
  'Je veux acheter un 2 chambres à Marina'      -> achat
  'Location à JVC ?'                            -> location
  'Mon voisin fait du bruit'                    -> humain
2. Éventail parallèle
  3 vérifications ; latence parallèle 5 s, séquentielle 10 s
3. Évaluateur-optimiseur
  manquant au 1er tour : ['charges']
  avis complet au tour 2
4. Exécution durable
  plantage avant notifier ; point de reprise : ['creer_offre', 'rediger', 'verifier']
  reprise : ['verifier', 'rediger', 'creer_offre', 'notifier'] ; offre OFFRE-001
5. Queue des latences
   1 ouvriers à 95 % sous 4 s : tous sous 4 s dans 0.950 des cas
   3 ouvriers à 95 % sous 4 s : tous sous 4 s dans 0.857 des cas
  10 ouvriers à 95 % sous 4 s : tous sous 4 s dans 0.599 des cas
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : orchestrer, c'est choisir le bon motif et rendre l'enchaînement robuste. Un routeur qui renvoie l'inconnu vers un humain, des ouvriers indépendants lancés ensemble, un évaluateur qui bloque un avis incomplet, et un état enregistré après chaque étape pour qu'un plantage ne fasse ni perdre ni refaire le travail.

### Mécanisme du programme, en détail

Le programme assemble trois motifs d'orchestration sur une demande immobilière. `router` lit la demande et l'envoie vers un traitement « achat », « location » ou « humain » à partir de mots-clés : c'est le routage, qui ne coûte presque rien et évite d'utiliser un agent généraliste pour tout. `eventail` lance en parallèle, avec un `ThreadPoolExecutor`, les trois ouvriers qui vérifient le titre de propriété, les charges et le prix, attend leurs trois résultats, puis renvoie aussi les deux durées simulées : le maximum des durées plus le temps d'agrégation en parallèle, la somme des durées plus l'agrégation en séquentiel. C'est la formule T_parallèle = max Tᵢ + T_agrégation, comparée à T_séquentiel = Σ Tᵢ + T_agrégation.

`boucle_eval_optim` est le motif évaluateur-optimiseur : l'évaluateur liste les rubriques qui manquent encore dans l'avis (titre, charges, prix), l'optimiseur les complète à partir des résultats des ouvriers, et la boucle s'arrête dès qu'il ne manque rien, ou après `max_tours` tours pour ne jamais tourner indéfiniment. `creer_offre` est l'étape à effet de bord du processus : elle reçoit une clé d'idempotence, et si cette clé a déjà produit une offre, elle renvoie la même offre au lieu d'en créer une seconde. La seconde partie du programme déroule le processus comme une exécution durable : après chaque étape terminée, l'orchestrateur enregistre un point de reprise. Il simule ensuite une panne avec l'exception `Plantage` au milieu d'une étape, puis relance le processus à partir du dernier point de reprise. Les étapes déjà terminées sont sautées, et l'étape interrompue est rejouée avec la même clé : le compteur d'appels de `creer_offre` augmente, mais une seule offre existe.

## Squelette algorithmique

```text
ALGORITHME TraiterUneDemande
ENTRÉES : demande, dossier, ouvriers (fonction, durée), T_agrégation, max_tours, clé d'idempotence
SORTIE  : l'offre créée, ou un transfert à un humain

  route ← Router(demande)
  SI route = « humain » ALORS RETOURNER transfert
  résultats ← lancer tous les ouvriers EN PARALLÈLE sur le dossier ; attendre tous les résultats
  T_par ← max(durées) + T_agrégation         T_seq ← Σ durées + T_agrégation
  avis ← brouillon
  POUR tour DE 1 À max_tours FAIRE
      manquantes ← Évaluateur(avis)
      SI manquantes vide ALORS sortir de la boucle
      avis ← Optimiseur(avis, manquantes, résultats)
  FIN POUR
  RETOURNER CréerOffre(clé)                   (idempotent : rejouée après une panne, elle ne double rien)

ALGORITHME CréerOffre(clé)
  SI clé ∉ offres ALORS offres[clé] ← nouvelle offre
  RETOURNER offres[clé]

ALGORITHME ExécutionDurable
ENTRÉES : étapes e₁ … e_n, magasin de points de reprise
  faites ← dernier point de reprise (ensemble des étapes terminées, et leurs résultats)
  POUR CHAQUE étape e DANS l'ordre FAIRE
      SI e ∈ faites ALORS passer                       (jamais refaite)
      résultat ← e()                                   (une panne ici interrompt tout)
      faites ← faites ∪ {e : résultat} ; enregistrer le point de reprise
  FIN POUR
  après une panne : relancer ExécutionDurable ; l'étape interrompue est rejouée, d'où l'idempotence
```

**Complexité.** Le temps de l'éventail est celui de l'ouvrier le plus lent, pas la somme : c'est le gain du parallélisme, payé par m appels simultanés. Si chaque ouvrier tient son délai avec la probabilité q, les m ouvriers le tiennent tous avec la probabilité qᵐ, la troisième formule du fichier. La boucle évaluateur-optimiseur fait au plus 2 × max_tours appels. `CréerOffre` coûte O(1) avec un dictionnaire.

**Du squelette au code.** `Router` correspond à `router`, l'éventail à `eventail` (avec `verifier_titre`, `verifier_charges` et `estimer_prix`), la boucle à `boucle_eval_optim` (avec `evaluateur` et `optimiseur`), et `CréerOffre` à `creer_offre`. La panne et la reprise sont simulées dans `main` avec `Plantage`.

## Cas d'usage réels aux Émirats

Les durées et volumes sont illustratifs.

### Immobilier — avis d'achat en parallèle

L'agence de l'exemple traite 300 demandes d'avis par mois. Les trois vérifications parallèles ramènent le délai de réponse de 10 à 5 secondes par dossier, sans changer la facture d'API. L'évaluateur garantit que l'avis contient les trois rubriques avant envoi ; un avis sans les charges de copropriété a déjà coûté à l'agence un litige avec un acheteur.

### Banque — ouverture de compte entreprise

L'ouverture d'un compte pour une société de free zone dure plusieurs jours : collecte des pièces, contrôle KYC des bénéficiaires effectifs, filtrage des sanctions, validation par un analyste. Le flux est durable : chaque étape terminée est enregistrée, l'attente de l'analyste peut durer deux jours, et un redéploiement de l'application au milieu ne relance ni le filtrage déjà fait ni l'envoi de la demande de pièces, qui est idempotent.

### Secteur public — demandes bilingues

Un service public reçoit des demandes en arabe et en anglais. Un routeur classe chaque demande vers l'un des quatre traitements connus ; tout ce qui sort de ces quatre catégories va vers un agent humain plutôt que vers une route « par défaut ». Le taux de demandes routées vers l'humain est suivi : quand il monte, c'est le signal qu'une nouvelle catégorie de demandes est apparue.

## Pièges et limites

- **Passer en multi-agent par défaut.** Plus d'agents, c'est plus de tokens, plus de latence et des erreurs corrélées ; on commence par un workflow.
- **Une route par défaut.** Une demande mal classée part dans le mauvais traitement sans que personne le voie ; l'inconnu va vers un humain.
- **Paralléliser des étapes dépendantes.** L'ouvrier du prix n'a pas besoin du titre, mais l'avis a besoin des trois : seules les étapes vraiment indépendantes partent ensemble.
- **Enregistrer l'état avant l'effet de bord.** Si le point de reprise dit « offre créée » alors que la création a planté, la reprise saute une offre jamais créée ; on enregistre **après**, et l'étape est idempotente pour supporter la répétition.
- **Ignorer la queue.** Dix ouvriers « rapides à 95 % » donnent un éventail lent dans 40 % des cas.

### Exercice feuille blanche

1. Réécrire `Durable.executer` et `reprendre`, puis simuler un plantage avant `rediger` : quelles étapes sont refaites à la reprise ?
2. Calculer la latence en séquence et en parallèle de quatre ouvriers de 1,5 ; 2 ; 2 et 6 secondes avec une agrégation de 0,5 seconde, puis dire lequel optimiser en premier. (Réponse : 12 s et 6,5 s ; celui de 6 secondes, qui est le chemin critique.)
3. Trouver le bug : `creer_offre` génère un nouvel identifiant à chaque appel, sans clé. Que produit une reprise après un plantage survenu juste après la création de l'offre mais avant l'écriture du point de reprise ? (Réponse : deux offres pour le même dossier.)

## Pour aller plus loin

- Décider quelle tâche passe en premier quand plusieurs attendent : [étape 41](<41-Orchestration-Formule-Score-de-Priorite.md>).
- Le graphe des dépendances, son ordre d'exécution et la détection de cycle : étapes 42 à 45.
- Le coût en tokens d'un système à plusieurs agents et la file d'attente des ouvriers : étapes 68 à 72.

> Suite : [Score de priorité de tâche](<41-Orchestration-Formule-Score-de-Priorite.md>) — étape 41.
