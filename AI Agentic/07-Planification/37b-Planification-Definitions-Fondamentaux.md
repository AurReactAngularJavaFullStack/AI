# Étape 37 bis — Planification — Définitions fondamentales : décider de la suite

> Étape 37 bis du parcours · Prérequis : [Transformer : formules manquantes](<../06-Attention-et-Transformer/37-Transformer-Formules-de-Liaison.md>) · Suite : [Agent et planification : MDP](<38-Agent-et-Planification-MDP-Bellman.md>)

**Dossier :** 07-Planification  
**Métiers :** AI Engineers, Product Engineers, Forward-Deployed Engineers

Planifier, pour un agent, c'est décider de la suite avant de la faire : quelles étapes, dans quel ordre, avec quels outils, et quoi faire si une étape échoue. Ce fichier pose le vocabulaire de la planification des agents à base de modèles de langage, avant les deux outils mathématiques du dossier : Bellman (étape 38), qui juge une action par ses conséquences, et A* (étape 40), qui trouve le chemin le moins cher dans un graphe connu. Il construit ensuite un planificateur-exécutant qui valide le plan avant de l'exécuter, replanifie après un échec et demande une approbation humaine avant l'action sensible.

## Définitions

### Agir pas à pas ou planifier d'abord

Un agent **réactif** (ReAct, étape 1) décide une action à la fois : il agit, observe, puis choisit la suivante. Il s'adapte bien à ce qu'il découvre, mais ne voit pas loin et peut tourner en rond. Un agent **délibératif** (Plan-and-Execute) produit d'abord un plan complet, puis l'exécute. Le plan se lit, se valide et s'approuve avant toute action ; il coûte moins d'appels au modèle, puisque l'exécution peut être du code ordinaire. Les deux se combinent : un plan général, et du ReAct à l'intérieur d'une étape difficile.

### Décomposition

Décomposer un objectif, c'est le couper en sous-tâches assez petites pour qu'un outil ou un appel au modèle les accomplisse, avec leurs **dépendances** : l'étape 2 utilise le résultat de l'étape 1. Les dépendances forment un graphe ; il doit être sans cycle, ce que l'étape 44 (tri topologique) vérifie en général.

### Le plan est une donnée

Un plan utile n'est pas un paragraphe : c'est un objet structuré, contraint par un schéma (étape 8). Chaque étape a un identifiant, un outil, des arguments, la liste des étapes dont elle dépend et, si besoin, une marque `sensible`. Un argument peut faire référence au résultat d'une étape précédente (`"$1.fournisseur"`), ce qui rend le flux de données explicite.

### Validation du plan

Avant d'exécuter, le programme vérifie le plan, sans modèle :

- chaque outil existe et l'agent a le droit de l'appeler ;
- chaque dépendance pointe vers une étape **antérieure** ;
- chaque référence `$k.champ` vise une étape dont on dépend ;
- le nombre d'étapes reste dans le budget.

Un plan refusé repart vers le modèle avec la liste des erreurs, comme une sortie structurée invalide à l'étape 8.

### Replanification

Le monde ne suit pas toujours le plan : un fournisseur est en rupture, une API renvoie une erreur, une donnée manque. L'exécutant s'arrête alors à l'étape fautive, renvoie au planificateur le plan, les résultats déjà obtenus et l'erreur, et reçoit un plan corrigé. Le nombre de replanifications est borné, sinon un objectif impossible fait boucler l'agent.

### Approbation humaine

Une étape marquée `sensible` (créer un bon de commande, envoyer un e-mail à un client, modifier un dossier) ne s'exécute qu'après l'accord d'un humain ou d'une règle d'approbation. Le plan rend cette approbation possible **avant** l'action : l'humain voit l'étape et ses arguments résolus, pas une intention vague.

### Critères d'arrêt

Un agent planificateur s'arrête quand l'objectif est atteint, quand le budget (étapes, replanifications, coût) est épuisé, quand un humain refuse, ou quand continuer coûte plus que ce que l'information supplémentaire rapporterait (valeur de l'information, support Genspark §21).

### Où se placent Bellman et A\*

Un modèle de langage ne résout pas d'équation de Bellman et ne lance pas d'A\* pour planifier. Ces deux outils servent à des **sous-problèmes** bien posés : Bellman pour comparer des actions dont les conséquences s'étalent dans le temps (attendre une information ou agir maintenant), A\* pour trouver un chemin optimal dans un graphe connu (tournée de livraison, enchaînement d'étapes de coût connu). Ils se branchent comme des outils déterministes, que le plan appelle.

## Équations

Si un plan de n étapes réussit seulement quand chaque étape réussit, avec des probabilités pᵢ indépendantes (étape 1) :

$$
P_{\text{plan}} = \prod_{i=1}^{n} p_i
$$

Si l'agent peut replanifier jusqu'à R fois après un échec et que chaque nouveau plan réussit indépendamment avec la même probabilité :

$$
P(\text{succès}) = 1 - (1 - P_{\text{plan}})^{R+1}
$$

### Décryptage des symboles

$$
n
$$

**Sens :** nombre d'étapes du plan · **Variable Python :** `len(plan["etapes"])`

$$
p_i
$$

**Sens :** probabilité que l'étape i réussisse · **Variable Python :** —

$$
P_{\text{plan}}
$$

**Sens :** probabilité qu'un plan aille au bout · **Variable Python :** `p_plan`

$$
R
$$

**Sens :** nombre maximal de replanifications · **Variable Python :** `max_replans`

## Démonstration

**Le produit.** C'est la fiabilité composée de l'étape 1 : la probabilité que toutes les étapes réussissent vaut le produit des probabilités quand elles sont indépendantes.

**Les replanifications.** L'agent échoue au final seulement si les R + 1 tentatives échouent toutes. Chaque tentative échoue avec la probabilité 1 − Pₚₗₐₙ ; par indépendance, toutes échouent avec la probabilité (1 − Pₚₗₐₙ)ᴿ⁺¹, et l'événement contraire, « au moins une réussit », a pour probabilité 1 − (1 − Pₚₗₐₙ)ᴿ⁺¹.

**Exemple à la main.** Un plan de 6 étapes fiables à 95 % : 0,95⁶ = 0,9025³ = 0,735092. Avec R = 2 replanifications :

$$
1 - 0{,}264908^3 = 1 - 0{,}018590 = 0{,}9814 .
$$

**La limite de l'hypothèse.** Replanifier aide quand l'échec vient d'une cause que le nouveau plan contourne (un fournisseur en rupture, un autre en stock). Si l'échec vient d'un objectif impossible ou d'un outil cassé, toutes les tentatives échouent ensemble : les échecs sont corrélés et la formule surestime. C'est pour cela que R reste petit (1 à 3) et que l'échec final part vers un humain.

## Architecture hexagonale : planificateur et exécutant sont séparés

Le **planificateur** est un port vers le modèle : il reçoit l'objectif, la liste des outils et, après un échec, le contexte de l'échec ; il renvoie un plan. L'**exécutant** est du code du domaine : il valide, résout les références, appelle les outils, demande les approbations. On peut ainsi tester tout l'exécutant avec un faux planificateur, et changer de modèle sans toucher aux règles de validation.

## Construire depuis une feuille blanche

On construit l'agent d'approvisionnement d'un chantier à Dubaï, chargé de commander 50 tonnes de ciment. Le faux planificateur propose d'abord un plan avec un outil inexistant, qui est refusé à la validation ; puis un plan valide chez un fournisseur en rupture, qui échoue à l'exécution ; puis un plan chez un autre fournisseur, qui réussit après approbation du bon de commande. Un second scénario montre un refus d'approbation, un troisième un plan qui dépend d'une étape future.

### Déroulé, ligne par ligne

**Les outils.** `verifier_stock(fournisseur, article, quantite)` lève `RuntimeError` en cas de rupture ; `demander_devis` renvoie le montant (quantité × prix à la tonne) ; `creer_bon_commande` renvoie un numéro de bon. `SENSIBLES` contient `creer_bon_commande`.

**`valider_plan(plan, max_etapes)`** renvoie une liste d'erreurs : outil inconnu, identifiants non consécutifs, dépendance vers une étape non antérieure, référence `$k.champ` vers une étape dont on ne dépend pas, plan trop long.

**`resoudre(args, resultats)`** remplace chaque chaîne `"$k.champ"` par `resultats[k][champ]`. Pour l'étape 3, `{"fournisseur": "$2.fournisseur", "montant_aed": "$2.montant_aed"}` devient `{"fournisseur": "Al Ain Cement", "montant_aed": 16250}`.

**`executer_plan(planificateur, objectif, approbateur, max_replans)`** :

1. demande un plan ; s'il est invalide, renvoie les erreurs au planificateur (cela compte comme une tentative de plus) ;
2. exécute les étapes dans l'ordre ; avant une étape sensible, appelle `approbateur(outil, args)` ; un refus arrête tout avec le statut `refuse_humain` ;
3. si un outil lève une exception, renvoie l'erreur au planificateur et replanifie, au plus `max_replans` fois ;
4. renvoie le statut, les résultats, le nombre de plans demandés et de replanifications.

**`approbateur_seuil(plafond)`** fabrique une règle d'approbation : un bon de commande au-delà de `plafond` AED est refusé. En production, c'est un humain dans une interface, ou une règle de délégation de signature.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier_stock(fournisseur, article, quantite)`** — Cet outil joue le magasinier qu'on appelle avant de passer commande : il reçoit le nom d'un fournisseur, un article et une quantité, consulte le dictionnaire `STOCK` et lève une `RuntimeError` « rupture de stock » si la quantité disponible, zéro par défaut, est inférieure à celle demandée. Sinon, il renvoie un petit dictionnaire qui rappelle le fournisseur et indique `disponible` à vrai ; dans le scénario 1, le premier fournisseur n'a aucune tonne et fait échouer l'exécution, alors que le second en a 200, assez pour les 50 tonnes de ciment.

**`demander_devis(fournisseur, article, quantite)`** — C'est le commercial qui répond par un chiffre : l'outil reçoit le fournisseur, l'article et la quantité, multiplie la quantité par le prix à la tonne du fournisseur lu dans `PRIX_TONNE`, et renvoie un dictionnaire qui contient le fournisseur et le montant en dirhams. Pour 50 tonnes à 325 AED, il annonce 16 250 AED ; c'est ce montant que l'étape suivante du plan récupère par la référence `$2.montant_aed` et que l'approbateur compare à son plafond.

**`creer_bon_commande(fournisseur, montant_aed)`** — Cet outil est le service des achats qui signe pour de vrai, et c'est pour cela qu'il figure seul dans `SENSIBLES` : il reçoit le fournisseur et le montant, ajoute ce couple à la liste globale `BONS`, puis renvoie un numéro de bon formé à partir du nombre de bons déjà émis, `BC-0001` pour le premier. Comme il agit sur le monde, l'exécutant ne l'appelle qu'après accord de l'approbateur ; `main` vérifie qu'un seul bon existe à la fin, même après le scénario du refus.

**`valider_plan(plan, max_etapes)`** — On peut l'imaginer en contrôleur qui relit un ordre de mission avant de laisser partir quiconque : la fonction reçoit le plan, un dictionnaire dont la clé `etapes` contient la liste des étapes, et un budget de 6 étapes par défaut, puis vérifie que le plan n'est pas trop long, que les identifiants se suivent à partir de 1, que chaque outil existe dans `OUTILS`, que chaque dépendance pointe vers une étape antérieure et que chaque référence `$k.champ` vise une étape déclarée dans `depend_de`. Elle renvoie la liste des erreurs, vide si tout va bien ; elle refuse ainsi l'outil inconnu `payer_fournisseur` du scénario 1 et la dépendance vers une étape future du scénario 3.

**`resoudre(args, resultats)`** — Cette fonction est le secrétaire qui remplace, dans un formulaire, chaque renvoi « voir la pièce 2 » par la valeur écrite sur cette pièce : elle reçoit les arguments d'une étape et le dictionnaire des résultats des étapes déjà exécutées, reconnaît chaque chaîne de la forme `$k.champ` grâce à l'expression régulière `REF`, et la remplace par le champ demandé du résultat de l'étape k, en laissant les autres valeurs telles quelles. Elle renvoie le nouveau dictionnaire d'arguments ; pour l'étape 3, les deux références deviennent le nom du fournisseur et le montant 16 250 calculés à l'étape 2.

**`executer_plan(planificateur, objectif, approbateur, max_replans)`** — C'est le chef de chantier qui ne fait confiance au plan qu'après l'avoir lu, et qui sait quand renoncer : la fonction reçoit le planificateur, l'objectif, l'approbateur et le nombre maximal de replanifications, 2 par défaut, puis boucle en demandant un plan, en renvoyant les erreurs de `valider_plan` au planificateur s'il y en a, et sinon en exécutant les étapes dans l'ordre après avoir résolu leurs références. Avant une étape sensible, elle consulte l'approbateur et s'arrête avec le statut `refuse_humain` en cas de refus ; si un outil lève une `RuntimeError`, elle replanifie, ou renvoie le statut `echec` quand le budget est épuisé. Elle renvoie un dictionnaire de statut, avec les résultats, le nombre de plans demandés et de replanifications : 3 plans et 1 replanification dans le scénario 1.

**`etape(i, outil, args, depend_de)`** — Ce petit utilitaire est le formulaire pré-imprimé qui évite de recopier quatre clés à chaque ligne d'un plan : il reçoit le numéro de l'étape, le nom de l'outil, le dictionnaire des arguments et, facultativement, les numéros des étapes dont elle dépend, vide par défaut. Il renvoie le dictionnaire de l'étape, avec `id`, `outil`, `args` et `depend_de` converti en liste ; `plan_chez` et `main` s'en servent pour écrire à la main les plans valides et invalides que le faux planificateur récitera.

**`plan_chez(fournisseur)`** — Cette fonction rédige, pour un fournisseur donné, le plan type en trois étapes qu'un modèle aurait pu proposer : elle reçoit le nom du fournisseur et construit la vérification du stock de 50 tonnes de `ciment_OPC`, puis la demande de devis qui reprend le fournisseur de l'étape 1 par `$1.fournisseur`, enfin le bon de commande qui reprend fournisseur et montant de l'étape 2. Elle renvoie ce plan sous forme de chaîne JSON, comme le ferait un vrai modèle, et `executer_plan` doit donc le décoder avec `json.loads` avant de le valider.

**`FauxPlanificateur.__init__(script)`** — Le constructeur prépare un comédien qui jouera le rôle du modèle de langage en récitant un texte appris d'avance : il reçoit la liste des plans à proposer, dans l'ordre, en fait une copie qu'il range dans `script`, et crée la liste vide `recus`, qui notera tout ce que l'exécutant lui dira. Il ne renvoie rien ; grâce à ce faux planificateur, on peut tester l'exécutant de bout en bout sans appeler aucun modèle, comme le permet l'architecture hexagonale décrite plus haut.

**`FauxPlanificateur.__call__(objectif, retour)`** — Cette méthode est la réplique du comédien chaque fois que l'exécutant lui donne la parole : elle reçoit l'objectif et le retour de la tentative précédente, `None` la première fois, puis un message d'erreur de validation ou d'exécution, ajoute ce retour à `recus` et renvoie le premier plan restant du script, qu'elle retire de la liste. `main` relit ensuite `recus` pour vérifier que le planificateur a bien reçu « Plan refusé : étape 1 : outil inconnu 'payer_fournisseur' », puis le message de rupture de stock.

**`approbateur_seuil(plafond)`** — C'est la fabrique de signataires : la fonction reçoit un plafond en dirhams et renvoie une petite fonction anonyme qui, pour un outil et ses arguments déjà résolus, répond vrai si le montant ne dépasse pas ce plafond et faux sinon. Avec un plafond de 20 000 AED, le bon de 16 250 AED est accepté dans le scénario 1 ; avec un plafond de 10 000 AED, il est refusé dans le scénario 2, et l'exécutant s'arrête à l'étape 3 sans créer de nouveau bon.

**`main()`** — Le chef d'orchestre joue les quatre scènes du chapitre : un faux planificateur propose d'abord un plan invalide, puis un plan chez un fournisseur en rupture, puis un plan qui réussit, et l'on vérifie 3 plans demandés, 1 replanification, un devis de 16 250 AED et un seul bon créé. Il rejoue ensuite le plan gagnant avec un plafond trop bas pour obtenir `refuse_humain`, fait valider un plan qui dépend d'une étape future, et recalcule enfin les formules, 0,95⁶ = 0,735092 et 0,9814 avec deux replanifications ; il ne renvoie rien et n'imprime le message final que si tous les `assert` passent.

```python
"""Étape 37 bis — planifier puis exécuter : plan structuré, validation, références, replanification, approbation."""
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STOCK = {("Gulf Cement", "ciment_OPC"): 0, ("Al Ain Cement", "ciment_OPC"): 200}
PRIX_TONNE = {"Gulf Cement": 310, "Al Ain Cement": 325}
BONS = []


def verifier_stock(fournisseur: str, article: str, quantite: int) -> dict:
    if STOCK.get((fournisseur, article), 0) < quantite:
        raise RuntimeError(f"rupture de stock : {article} chez {fournisseur}")
    return {"fournisseur": fournisseur, "disponible": True}


def demander_devis(fournisseur: str, article: str, quantite: int) -> dict:
    return {"fournisseur": fournisseur, "montant_aed": quantite * PRIX_TONNE[fournisseur]}


def creer_bon_commande(fournisseur: str, montant_aed: float) -> dict:
    BONS.append((fournisseur, montant_aed))
    return {"bon": f"BC-{len(BONS):04d}"}


OUTILS = {"verifier_stock": verifier_stock, "demander_devis": demander_devis,
          "creer_bon_commande": creer_bon_commande}
SENSIBLES = {"creer_bon_commande"}
REF = re.compile(r"^\$(\d+)\.(\w+)$")


def valider_plan(plan: dict, max_etapes: int = 6) -> list[str]:
    erreurs, etapes = [], plan.get("etapes", [])
    if len(etapes) > max_etapes:
        erreurs.append(f"plan de {len(etapes)} étapes > budget {max_etapes}")
    for rang, e in enumerate(etapes, start=1):
        if e["id"] != rang:
            erreurs.append(f"étape {e['id']} : identifiant attendu {rang}")
        if e["outil"] not in OUTILS:
            erreurs.append(f"étape {e['id']} : outil inconnu {e['outil']!r}")
        for d in e.get("depend_de", []):
            if d >= e["id"]:
                erreurs.append(f"étape {e['id']} : dépend de l'étape {d}, qui n'est pas antérieure")
        for v in e["args"].values():
            m = REF.match(v) if isinstance(v, str) else None
            if m and int(m.group(1)) not in e.get("depend_de", []):
                erreurs.append(f"étape {e['id']} : référence {v} sans dépendance déclarée")
    return erreurs


def resoudre(args: dict, resultats: dict) -> dict:
    sortie = {}
    for cle, v in args.items():
        m = REF.match(v) if isinstance(v, str) else None
        sortie[cle] = resultats[int(m.group(1))][m.group(2)] if m else v
    return sortie


def executer_plan(planificateur, objectif: str, approbateur, max_replans: int = 2) -> dict:
    retour, plans, replans = None, 0, 0
    while True:
        plan = json.loads(planificateur(objectif, retour))
        plans += 1
        erreurs = valider_plan(plan)
        if erreurs:
            retour = "Plan refusé : " + " ; ".join(erreurs)
            continue
        resultats = {}
        try:
            for e in plan["etapes"]:
                args = resoudre(e["args"], resultats)
                if e["outil"] in SENSIBLES and not approbateur(e["outil"], args):
                    return {"statut": "refuse_humain", "etape": e["id"], "args": args, "plans": plans}
                resultats[e["id"]] = OUTILS[e["outil"]](**args)
            return {"statut": "fini", "resultats": resultats, "plans": plans, "replans": replans}
        except RuntimeError as err:
            if replans == max_replans:
                return {"statut": "echec", "erreur": str(err), "plans": plans, "replans": replans}
            replans += 1
            retour = f"Échec à l'exécution : {err}. Propose un autre plan."


def etape(i, outil, args, depend_de=()):
    return {"id": i, "outil": outil, "args": args, "depend_de": list(depend_de)}


def plan_chez(fournisseur: str) -> str:
    return json.dumps({"etapes": [
        etape(1, "verifier_stock", {"fournisseur": fournisseur, "article": "ciment_OPC", "quantite": 50}),
        etape(2, "demander_devis", {"fournisseur": "$1.fournisseur", "article": "ciment_OPC", "quantite": 50}, [1]),
        etape(3, "creer_bon_commande", {"fournisseur": "$2.fournisseur", "montant_aed": "$2.montant_aed"}, [2]),
    ]})


class FauxPlanificateur:
    def __init__(self, script):
        self.script, self.recus = list(script), []

    def __call__(self, objectif, retour):
        self.recus.append(retour)
        return self.script.pop(0)


def approbateur_seuil(plafond: float):
    return lambda outil, args: args["montant_aed"] <= plafond


def main() -> None:
    plan_invalide = json.dumps({"etapes": [etape(1, "payer_fournisseur", {"montant_aed": 15500})]})
    print("1. Plan invalide, puis rupture, puis succès")
    planif = FauxPlanificateur([plan_invalide, plan_chez("Gulf Cement"), plan_chez("Al Ain Cement")])
    r = executer_plan(planif, "Commander 50 t de ciment OPC", approbateur_seuil(20_000))
    for retour in planif.recus[1:]:
        print(f"  le planificateur reçoit : {retour}")
    print(f"  statut {r['statut']} ; {r['plans']} plans demandés, {r['replans']} replanification ; "
          f"devis {r['resultats'][2]['montant_aed']} AED ; {r['resultats'][3]['bon']}")
    assert r["statut"] == "fini" and r["plans"] == 3 and r["replans"] == 1
    assert r["resultats"][2] == {"fournisseur": "Al Ain Cement", "montant_aed": 16250}
    assert BONS == [("Al Ain Cement", 16250)]
    assert planif.recus[1] == "Plan refusé : étape 1 : outil inconnu 'payer_fournisseur'"

    print("2. Approbation refusée")
    r = executer_plan(FauxPlanificateur([plan_chez("Al Ain Cement")]), "…", approbateur_seuil(10_000))
    print(f"  statut {r['statut']} à l'étape {r['etape']}, montant présenté {r['args']['montant_aed']} AED")
    assert r["statut"] == "refuse_humain" and len(BONS) == 1                # aucun nouveau bon créé

    print("3. Dépendance vers une étape future")
    futur = {"etapes": [etape(1, "demander_devis", {"fournisseur": "$2.fournisseur", "article": "x", "quantite": 1}, [2]),
                        etape(2, "verifier_stock", {"fournisseur": "Gulf Cement", "article": "x", "quantite": 1})]}
    erreurs = valider_plan(futur)
    print(f"  {erreurs}")
    assert erreurs == ["étape 1 : dépend de l'étape 2, qui n'est pas antérieure"]

    print("4. Formules")
    p_plan = 0.95 ** 6
    p_final = 1 - (1 - p_plan) ** 3
    print(f"  P_plan = 0,95^6 = {p_plan:.6f} ; avec R = 2 : {p_final:.4f}")
    assert round(p_plan, 6) == 0.735092 and round(p_final, 4) == 0.9814
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Plan invalide, puis rupture, puis succès
  le planificateur reçoit : Plan refusé : étape 1 : outil inconnu 'payer_fournisseur'
  le planificateur reçoit : Échec à l'exécution : rupture de stock : ciment_OPC chez Gulf Cement. Propose un autre plan.
  statut fini ; 3 plans demandés, 1 replanification ; devis 16250 AED ; BC-0001
2. Approbation refusée
  statut refuse_humain à l'étape 3, montant présenté 16250 AED
3. Dépendance vers une étape future
  ["étape 1 : dépend de l'étape 2, qui n'est pas antérieure"]
4. Formules
  P_plan = 0,95^6 = 0.735092 ; avec R = 2 : 0.9814
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : la planification d'un agent est fiable quand le plan est une donnée. Le code le valide avant d'agir, résout les références entre étapes, soumet l'action sensible à une approbation sur des arguments concrets, et replanifie un nombre borné de fois quand le monde ne suit pas.

### Mécanisme du programme, en détail

Le programme sépare nettement celui qui propose (le planificateur, un faux modèle qui renvoie un plan JSON) de celui qui exécute (le code). `valider_plan` relit tout le plan avant la moindre action : il refuse un plan plus long que le budget d'étapes, une étape dont l'identifiant n'est pas son rang, un outil absent du registre, une dépendance vers une étape qui n'est pas antérieure, et une référence `@k.champ` utilisée sans que l'étape k soit déclarée dans `depend_de`. Un plan refusé n'est jamais exécuté ; la liste de ses erreurs est renvoyée au planificateur, qui propose un nouveau plan.

`resoudre` remplace, juste avant l'exécution d'une étape, chaque référence `@k.champ` par la valeur du champ dans le résultat de l'étape k : c'est ce qui permet à une étape d'utiliser le prix trouvé par une étape précédente sans repasser par le modèle. `executer_plan` enchaîne les deux : il demande un plan, le valide, exécute les étapes dans l'ordre, et s'arrête avant toute étape sensible (la création d'un bon de commande) si l'approbateur la refuse ; `approbateur_seuil` modélise une règle simple, approuver seulement sous un plafond de montant. Si un outil échoue à l'exécution, la fonction demande un nouveau plan en expliquant l'échec, au plus `max_replans` fois, puis abandonne avec le statut `echec`.

## Squelette algorithmique

```text
ALGORITHME PlanifierPuisExécuter
ENTRÉES : planificateur, objectif, outils, outils sensibles, approbateur, budget d'étapes, max_replans
SORTIE  : (statut, résultats)

  retour ← aucun ; replans ← 0
  BOUCLE
      plan ← planificateur(objectif, retour)
      erreurs ← ValiderPlan(plan, budget)
      SI erreurs non vide ALORS retour ← erreurs ; recommencer la BOUCLE
      résultats ← vide
      essayer
          POUR CHAQUE étape e DU plan FAIRE
              arguments ← Résoudre(e.arguments, résultats)          (remplace les @k.champ)
              SI e.outil est sensible ET approbateur(e.outil, arguments) = faux ALORS
                  RETOURNER (« refusé par l'humain », e)
              résultats[e.id] ← outils[e.outil](arguments)
          FIN POUR
          RETOURNER (« fini », résultats)
      en cas d'échec d'un outil :
          SI replans = max_replans ALORS RETOURNER (« échec », erreur)
          replans ← replans + 1 ; retour ← « échec à l'exécution : … propose un autre plan »
  FIN BOUCLE
```

**Complexité.** La validation coûte O(n × a) pour n étapes de a arguments chacune. L'exécution coûte n appels d'outils au plus par plan. Le nombre d'appels au planificateur est 1 + (plans refusés) + replans, borné par `max_replans` pour les échecs d'exécution. La fiabilité suit la formule du fichier : un plan de n étapes réussit avec la probabilité Π pᵢ, et R replans la portent à 1 − (1 − Π pᵢ)^(R+1).

**Du squelette au code.** `ValiderPlan` correspond à `valider_plan`, `Résoudre` à `resoudre`, la boucle à `executer_plan`, l'approbateur à `approbateur_seuil`, et les outils à `verifier_stock`, `demander_devis` et `creer_bon_commande` (le seul sensible). `etape` et `plan_chez` fabriquent les plans du faux planificateur.

## Cas d'usage réels aux Émirats

Les montants et règles d'approbation sont illustratifs.

### BTP — approvisionnement de chantier

Un groupe de construction à Dubaï fait planifier ses commandes de matériaux par un agent. Le plan est affiché au conducteur de travaux avant toute action : vérifications de stock, devis, puis bon de commande. La délégation de signature est codée dans l'approbateur (jusqu'à 50 000 AED pour un conducteur, au-delà pour le directeur de projet), et une rupture chez un fournisseur déclenche une replanification vers la liste des fournisseurs agréés, jamais vers un fournisseur inconnu.

### RH — intégration d'un nouveau salarié

Un cabinet RH planifie l'intégration d'un salarié venant de l'étranger : contrat, visa de travail, Emirates ID, ouverture du compte de paie compatible WPS, formation. Les dépendances sont strictes (pas de compte de paie avant l'Emirates ID). Le plan validé par code évite qu'un modèle propose de commencer la paie avant la fin des démarches, et chaque étape qui écrit dans un système externe est marquée sensible.

### Assurance — instruction d'un sinistre complexe

Un assureur auto planifie l'instruction d'un sinistre avec tiers : récupérer le constat de police, l'expertise du garage, la police du tiers, puis calculer le recours. Quand le constat n'est pas encore disponible, l'exécutant ne force pas : il replanifie en mettant le dossier en attente et en programmant une relance, et la limite de replanifications renvoie les dossiers bloqués vers un gestionnaire.

## Pièges et limites

- **Exécuter un plan non validé.** Un outil inventé ou une dépendance circulaire se découvrent alors au milieu de l'exécution, après des effets de bord.
- **Replanifier sans limite.** Un objectif impossible fait tourner l'agent et la facture.
- **Demander une approbation sur une intention.** « Puis-je commander du ciment ? » n'est pas approuvable ; « bon de commande de 16 250 AED à Al Ain Cement » l'est.
- **Planifier trop finement.** Un plan de 25 étapes accumule les échecs (0,95²⁵ ≈ 0,28) ; mieux vaut moins d'étapes, plus robustes.
- **Croire que replanifier corrige tout.** Les échecs corrélés (objectif impossible, outil cassé) font échouer toutes les tentatives.

### Exercice feuille blanche

1. Réécrire `valider_plan` avec ses quatre règles et la tester sur un plan de trois étapes valide, puis sur une dépendance circulaire 1 → 2 → 1.
2. Calculer P(succès) pour 4 étapes à 0,9 et R = 1. (Réponse : 0,9⁴ = 0,6561 ; 1 − 0,3439² = 0,8817.)
3. Ajouter un budget de coût : le plan est refusé si la somme des devis estimés dépasse le budget du lot.

## Pour aller plus loin

- Juger une action par ses conséquences futures, avec le facteur γ : [étape 38](<38-Agent-et-Planification-MDP-Bellman.md>).
- Le chemin le moins cher dans un graphe d'étapes : A\*, [étape 40](<40-Planification-Formule-A-Star.md>).
- Plusieurs agents et plusieurs plans qui s'ordonnent entre eux : l'orchestration, [étape 40 bis](<../08-Orchestration/40b-Orchestration-Definitions-Fondamentaux.md>).

> Suite : [Agent et planification : MDP](<38-Agent-et-Planification-MDP-Bellman.md>) — étape 38.
