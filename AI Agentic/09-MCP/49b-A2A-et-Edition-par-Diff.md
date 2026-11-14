# Étape 49 bis — MCP — A2A et édition par diff

**Dossier :** 09-MCP  
**Métiers concernés :** AI Agent Ops, Forward-Deployed Engineers, AI Platform Team

> Étape 49 bis du parcours · Prérequis : [Score de disponibilité d'un serveur MCP](<49-MCP-Formule-Score-de-Disponibilite.md>) · Suite : [Précision, rappel, F1 et KL](<../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>)

MCP relie un agent à ses **outils** (étape 46). Mais un agent a parfois besoin d'un autre **agent** : un orchestrateur confie une rédaction à un spécialiste, une vérification à un relecteur. Déléguer à un agent n'est pas appeler un outil : l'autre agent raisonne, peut demander une précision, travaille longtemps, et rend un résultat qui n'est pas une simple valeur mais un document ou un diagnostic. C'est ce que couvre **A2A** (Agent-to-Agent), un protocole agent ↔ agent. Ce fichier en construit, en bibliothèque standard et en mémoire, le squelette : une carte d'agent, une tâche avec son cycle de vie, des messages et des artefacts. Il traite ensuite une tâche concrète et fréquente — **éditer un document** — par la bonne technique : le remplacement à occurrence unique et le diff unifié, qui rendent l'édition déterministe et peu coûteuse en tokens.

## Définition

### A2A

A2A est un protocole qui fait communiquer deux agents, là où MCP fait communiquer un agent et ses outils. Un agent qui veut être joignable publie une **carte d'agent** (agent card) : une fiche en JSON qui dit son nom, sa description, sa version et ses **compétences** (skills), chacune avec un identifiant et une description. Un agent client découvre cette carte, choisit une compétence, et confie une **tâche** (task) : un objet qui porte un identifiant, un **état**, l'historique des **messages** échangés (chacun avec un rôle et des « parts », par exemple du texte) et les **artefacts** produits (le résultat du travail). La tâche suit un **cycle de vie** : elle est soumise, passe en cours, et se termine, échoue, ou réclame une entrée de l'utilisateur. Les noms d'états et de champs retenus ici sont **génériques** : selon la spécification publiée, à vérifier pour les noms exacts des états et des champs.

### Édition par diff

Faire réécrire un document entier par un modèle à chaque petite modification est coûteux (le modèle regénère tout) et risqué (il peut altérer une partie qu'il devait laisser intacte). L'**édition par diff** remplace cela par un outil `remplacer(fichier, ancien, nouveau)` qui n'agit que si le passage `ancien` apparaît **exactement une fois** : une occurrence unique rend l'édition déterministe, car il n'existe qu'une seule façon de l'appliquer. S'il apparaît zéro fois, l'outil refuse (introuvable) ; s'il apparaît plusieurs fois, il refuse (ambigu) et réclame plus de contexte. Le résultat est renvoyé sous forme de **diff unifié** (unified diff), le format produit par l'outil `diff` et compris par `patch` : seules les lignes changées et quelques lignes de contexte y figurent. Le modèle n'émet donc que le patch, pas le fichier entier, ce qui économise des tokens de sortie proportionnellement à la taille du fichier.

## Rôle dans un agent

Dans la boucle percevoir → décider → agir → observer, A2A intervient à l'étape « agir », quand l'agent décide de **déléguer**. Au lieu d'appeler un outil local, il envoie une tâche à un agent distant, exactement comme il enverrait un `tools/call` à un serveur MCP, mais la réponse n'est pas immédiate : elle peut passer par « entrée requise » et demander un aller-retour. La disponibilité de l'agent distant se mesure comme celle d'un serveur MCP (étape 49), et sa tâche peut elle-même appeler des outils MCP : les deux protocoles se complètent, A2A entre agents, MCP entre un agent et ses outils. L'édition par diff, elle, est la forme que prend le **résultat** d'une tâche d'écriture : un artefact compact et vérifiable. Elle sert partout où un agent modifie un texte long — un contrat, une configuration, un fichier de code — sans le réécrire en entier, ce qui réduit le coût (étape 72) et supprime le risque qu'il change une ligne qu'on ne lui avait pas demandé de toucher.

## Construire depuis une feuille blanche

Le programme joue deux agents en mémoire. L'**agent éditeur** publie une carte avec la compétence `editer_document` ; il reçoit une tâche, exécute `remplacer`, et renvoie le patch comme artefact. L'**agent orchestrateur** lit la carte (sérialisée en JSON, comme sur un réseau), vérifie la compétence, puis confie des tâches. On observe le cycle de vie complet sur quatre tâches : une édition unique réussie, une édition ambiguë refusée, la même réussie avec du contexte, et une édition dont le texte est introuvable, qui fait passer la tâche en « entrée requise ».

### Déroulé, ligne par ligne

**`Competence` et `CarteAgent`** sont les deux dataclasses de la carte. `CarteAgent.json()` sérialise la fiche avec `sort_keys=True`, pour que deux sérialisations du même agent soient identiques ; `competence(id_)` cherche une compétence par son identifiant. La carte est l'équivalent A2A de ce que `tools/list` est à MCP : la découverte de ce que l'autre côté sait faire.

**Le cycle de vie.** `SOUMISE`, `EN_COURS`, `ENTREE_REQUISE`, `TERMINEE`, `ECHOUEE`, `ANNULEE` sont les six états, aux noms génériques. `TRANSITIONS` est la table des passages autorisés : depuis `EN_COURS`, on peut aller vers `ENTREE_REQUISE`, `TERMINEE`, `ECHOUEE` ou `ANNULEE` ; les trois états finaux n'ont aucune suite. C'est une machine à états, comme la machine pending/running/succeeded/failed d'une tâche longue.

**`message(role, texte)`** fabrique un message générique : un rôle (`"user"` ou `"agent"`) et une liste de « parts », ici une seule part de texte.

**`Tache`** porte l'identifiant, l'état, la liste des messages, la liste des artefacts et l'historique des états. `aller_a(etat)` **refuse** une transition hors de `TRANSITIONS[self.etat]` en levant `ValueError` : aucune tâche ne saute de `ENTREE_REQUISE` à `TERMINEE` sans repasser par `EN_COURS`. `ajouter_artefact(nom, texte)` range un résultat sous forme de part de texte.

**`remplacer(contenu, ancien, nouveau)`** est le cœur de l'édition sûre. Elle compte les occurrences d'`ancien` : zéro lève `ErreurEdition("motif introuvable")`, plus d'une lève `ErreurEdition("motif ambigu : N occurrences, ajouter du contexte")`, et exactement une applique `str.replace`. Un motif vide est refusé d'emblée. **`remplacer_naif_premier`** est la variante fautive, `replace(..., 1)`, gardée pour le contre-exemple : elle change la première occurrence sans vérifier l'unicité.

**`diff_unifie(avant, apres, nom)`** appelle `difflib.unified_diff` avec `lineterm=""` : le patch ne contient que les lignes modifiées, préfixées de `-` ou `+`, et quelques lignes de contexte préfixées d'une espace, sous un en-tête de tronçon `@@ -l,n +l,n @@` qui situe la modification (ligne de départ et nombre de lignes). La sortie est déterministe.

**`tokens(texte)`** applique l'heuristique des étapes 4 et 72 : environ un token pour quatre caractères (illustratif). **`economie_tokens(fichier, patch)`** renvoie `tokens(fichier) - tokens(patch)`, les tokens de sortie économisés en émettant le patch plutôt que le fichier réécrit.

**`AgentEditeur.traiter(tache, instruction)`** fait passer la tâche à `EN_COURS`, tente `remplacer`, et selon le résultat : sur « introuvable » ajoute un message et passe à `ENTREE_REQUISE` ; sur « ambigu » passe à `ECHOUEE` ; sur succès, écrit le nouveau document, ajoute l'artefact patch et un message chiffrant l'économie, puis passe à `TERMINEE`.

**`AgentOrchestrateur.decouvrir(competence_id)`** relit la carte depuis son JSON et cherche la compétence ; absente, elle lève `RuntimeError`. **`confier(instruction)`** crée une tâche, l'envoie à l'agent distant et la renvoie.

**`main()`**, section par section. (1) Découverte de la carte et d'une compétence, puis échec sur une compétence absente. (2) Édition unique sur un document de 30 lignes : la tâche parcourt soumise → en cours → terminée, et le patch ne touche que `clause_15`. (3) L'économie de tokens : 653 caractères de fichier contre 231 de patch, soit 105 tokens de sortie économisés. (4) L'ambiguïté : « 90000 » apparaît deux fois (montant et dépôt), l'édition est refusée (`ECHOUEE`), la variante naïve change une seule ligne — la mauvaise peut l'être —, puis l'édition réussit avec le contexte de la ligne, sans toucher au montant. (5) Un texte introuvable fait passer la tâche en « entrée requise », et la transition directe vers « terminée » est refusée.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`CarteAgent.json()`** — Cette méthode est le héraut qui, avant chaque rencontre, déroule le parchemin officiel de l'agent : elle ne reçoit rien d'autre que la carte elle-même, rassemble dans un dictionnaire le nom, la description, la version et la liste des compétences, chacune réduite à son identifiant, son nom et sa description, puis sérialise le tout avec `json.dumps`, en gardant les accents (`ensure_ascii=False`) et en triant les clés (`sort_keys=True`). Elle renvoie cette chaîne JSON, identique d'une sérialisation à l'autre pour le même agent, et c'est sous cette forme que la carte voyage jusqu'à l'orchestrateur, qui la relit dans `decouvrir` comme si elle avait traversé un réseau.

**`CarteAgent.competence(id_)`** — Celle-ci joue le rôle du bibliothécaire à qui l'on tend une cote : elle reçoit l'identifiant d'une compétence, parcourt dans l'ordre la liste des compétences de la carte et renvoie le premier objet `Competence` dont l'identifiant correspond, grâce à `next` appliqué à un générateur. Si aucune ne convient, elle ne lève pas d'exception mais renvoie `None`, laissant l'appelant décider de la suite ; c'est la recherche directe sur l'objet carte, alors que `main` ne l'appelle pas et que l'orchestrateur refait la même recherche, à sa façon, sur la carte relue depuis son JSON.

**`message(role, texte)`** — Cette petite fonction est le secrétaire qui met chaque phrase sous enveloppe réglementaire avant de l'envoyer : elle reçoit un rôle, `"user"` pour celui qui demande ou `"agent"` pour celui qui répond, et un texte, puis renvoie un dictionnaire à deux clés, `role` et `parts`, où `parts` est une liste qui contient une seule part de type `"text"` portant ce texte. Elle ne vérifie rien et ne lève aucune exception ; elle sert partout où le programme fabrique un message A2A, aussi bien la demande initiale que `confier` place dans une nouvelle tâche que les réponses de l'agent éditeur, qui chiffrent l'économie de tokens ou réclament le passage exact.

**`Tache.__init__(id_, demande)`** — Le constructeur ouvre un dossier neuf au guichet des tâches, comme un greffier qui inscrit une affaire au rôle : il reçoit l'identifiant de la tâche, par exemple `"t1"`, et le message de demande, enregistre l'identifiant, place la tâche dans l'état « soumise », range la demande comme premier message, prépare une liste d'artefacts vide et ouvre l'historique des états avec « soumise ». Il ne renvoie rien et ne vérifie rien ; toute la vie ultérieure de la tâche, ses transitions comme ses résultats, s'écrira ensuite dans ces attributs.

**`Tache.aller_a(etat)`** — Cette méthode est l'aiguilleur de la machine à états : elle reçoit l'état vers lequel on veut faire passer la tâche, consulte la table `TRANSITIONS` à la ligne de l'état courant et lève une `ValueError` du type « transition interdite : entrée-requise → terminée » si le passage n'y figure pas. Si la transition est permise, elle met à jour l'état et l'ajoute à l'historique, sans rien renvoyer ; c'est grâce à elle que `main` peut vérifier des parcours comme soumise → en-cours → terminée, et constater qu'une tâche en attente d'entrée ne saute pas directement à la fin sans repasser par « en cours ».

**`Tache.ajouter_message(msg)`** — Celle-ci est le fil de la correspondance d'un dossier, sur lequel on enfile chaque lettre reçue ou envoyée : elle reçoit un message déjà formé par `message`, l'ajoute à la fin de la liste des messages de la tâche et ne renvoie rien. Elle ne contrôle ni le rôle ni le contenu ; c'est l'agent éditeur qui l'appelle dans `traiter` pour annoncer une édition appliquée avec son économie de tokens, une édition refusée pour ambiguïté ou un texte introuvable, et `main` lit ensuite le dernier message de la liste pour l'afficher.

**`Tache.ajouter_artefact(nom, texte)`** — Cette méthode est le magasinier qui range le produit fini sur l'étagère de la tâche : elle reçoit un nom, comme `config_bail.patch`, et un texte, les emballe dans un dictionnaire qui porte ce nom et une liste de parts réduite à une seule part de texte, sur le même modèle que les messages, puis ajoute ce paquet à la liste des artefacts sans rien renvoyer. Dans le programme, l'artefact rangé est toujours le patch au format diff unifié, que `main` va chercher dans `artefacts[0]` pour l'imprimer ligne à ligne et vérifier qu'il ne touche que la clause 15.

**`remplacer_naif_premier(contenu, ancien, nouveau)`** — C'est le contre-modèle, l'employé pressé qui corrige la première ligne venue sans se demander s'il y en a d'autres : elle reçoit le contenu, le passage à remplacer et le nouveau texte, appelle `str.replace` avec une limite de un, et renvoie le contenu modifié à la première occurrence rencontrée, sans compter les occurrences ni lever d'exception. Sur la fiche du locataire où « 90000 » apparaît deux fois, elle change le montant et laisse le dépôt, alors que la même opération menée sur le texte lu à l'envers changerait le dépôt : `main` vérifie que les deux résultats diffèrent, preuve que cette variante obéit à l'ordre de recherche et non à l'intention de l'édition.

**`tokens(texte)`** — Cette fonction est le métreur qui estime d'un coup d'œil la longueur d'un texte en tokens, sans ouvrir de tokenizer : elle reçoit une chaîne, divise son nombre de caractères par quatre et renvoie l'entier le plus proche obtenu par `round`, l'heuristique illustrative des étapes 4 et 72. Le document de 30 lignes, long de 653 caractères après l'édition, compte ainsi environ 163 tokens, et le patch de 231 caractères environ 58 ; ces deux mesures nourrissent `economie_tokens` et l'affichage de la section 3 de `main`.

**`economie_tokens(fichier, patch)`** — Celle-ci est le contrôleur de gestion qui compare deux devis, la réécriture complète du fichier et l'envoi du seul patch : elle reçoit le texte du fichier et celui du patch, mesure chacun avec `tokens`, et renvoie la différence, c'est-à-dire le nombre de tokens de sortie que le modèle n'a pas eu à générer. Sur l'exemple du programme, 163 − 58 donne 105 tokens économisés, chiffre que l'agent éditeur glisse dans son message de fin de tâche et que `main` vérifie par un `assert` ; le résultat deviendrait négatif si le patch était plus long que le fichier, ce que la fonction n'interdit pas.

**`AgentEditeur.__init__(documents)`** — Le constructeur installe l'agent éditeur dans son bureau, comme un archiviste à qui l'on confie les clés d'une armoire : il reçoit un dictionnaire qui associe un nom de document à son texte, le garde dans l'attribut `documents`, que l'agent modifiera en place à chaque édition réussie, et accroche à l'agent la carte publique `CARTE_EDITEUR`, qui annonce la compétence `editer_document`. Il ne renvoie rien ; `main` lui passe une copie de `DOCUMENTS` faite avec `dict(...)`, si bien que les éditions de la démonstration ne touchent pas le dictionnaire d'origine.

**`AgentOrchestrateur.__init__(distant)`** — Le constructeur prépare le chef de projet qui va déléguer le travail : il reçoit l'agent distant, ici l'agent éditeur, le mémorise dans l'attribut `distant` et règle à 1 le compteur `prochain_id`, d'où viendront les identifiants des tâches. Il ne renvoie rien et ne contacte pas encore l'agent distant ; c'est `decouvrir` qui lira sa carte et `confier` qui lui enverra, une à une, les tâches numérotées t1, t2, t3 et t4 de la démonstration.

**`AgentOrchestrateur.decouvrir(competence_id)`** — Cette méthode est l'émissaire qui lit l'affiche placardée à la porte de l'autre agent avant de frapper : elle reçoit l'identifiant de la compétence recherchée, demande la carte de l'agent distant sous forme de JSON, la relit avec `json.loads` comme si elle arrivait par le réseau, puis cherche dans sa liste de compétences celle dont l'identifiant correspond. Si elle la trouve, elle renvoie un objet `Competence` reconstruit à partir du dictionnaire ; sinon elle lève une `RuntimeError` qui nomme la compétence manquante, ce que `main` montre avec `editer_document`, trouvée, puis `virer_des_fonds`, absente.

**`AgentOrchestrateur.confier(instruction)`** — Celle-ci est le bon de commande que le chef de projet remplit et remet au spécialiste : elle reçoit une instruction d'édition, un dictionnaire qui nomme le document, le passage à remplacer et le nouveau texte, crée une `Tache` nommée « t » suivi du compteur, dont le message de demande, au rôle `"user"`, contient cette instruction sérialisée en JSON à clés triées, puis incrémente le compteur. Elle fait ensuite traiter la tâche par l'agent distant avec `traiter` et renvoie la tâche, qui porte désormais son état final, son historique et, en cas de succès, son artefact patch ; dans cette version en mémoire, l'appel est synchrone.

```python
"""Étape 49 bis — A2A (agent ↔ agent) et édition par diff : carte d'agent, cycle de vie, remplacement unique, patch."""
import difflib
import json
import sys
from dataclasses import dataclass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- A2A : la carte d'agent (capacités en JSON)
@dataclass
class Competence:
    id: str
    nom: str
    description: str


@dataclass
class CarteAgent:
    """Fiche publique d'un agent : qui il est, ce qu'il sait faire. L'équivalent A2A de tools/list côté MCP."""
    nom: str
    description: str
    version: str
    competences: list

    def json(self) -> str:
        corps = {"nom": self.nom, "description": self.description, "version": self.version,
                 "competences": [{"id": c.id, "nom": c.nom, "description": c.description} for c in self.competences]}
        return json.dumps(corps, ensure_ascii=False, sort_keys=True)

    def competence(self, id_: str) -> Competence | None:
        return next((c for c in self.competences if c.id == id_), None)


# ---------------------------------------------------------------- A2A : cycle de vie d'une tâche
# Noms d'états GÉNÉRIQUES. Selon la spécification publiée, à vérifier pour les noms exacts des états et des champs.
SOUMISE, EN_COURS, ENTREE_REQUISE, TERMINEE, ECHOUEE, ANNULEE = (
    "soumise", "en-cours", "entrée-requise", "terminée", "échouée", "annulée")
TRANSITIONS = {
    SOUMISE: {EN_COURS, ANNULEE},
    EN_COURS: {ENTREE_REQUISE, TERMINEE, ECHOUEE, ANNULEE},
    ENTREE_REQUISE: {EN_COURS, ANNULEE},
    TERMINEE: set(),            # états finaux : plus aucune transition
    ECHOUEE: set(),
    ANNULEE: set(),
}


def message(role: str, texte: str) -> dict:
    """Message A2A générique : un rôle et des « parts ». Ici une seule part de texte."""
    return {"role": role, "parts": [{"type": "text", "texte": texte}]}


class Tache:
    """Une tâche A2A : un identifiant, un état, l'historique des messages et des artefacts produits."""

    def __init__(self, id_: str, demande: dict):
        self.id = id_
        self.etat = SOUMISE
        self.messages = [demande]
        self.artefacts: list = []
        self.historique = [SOUMISE]

    def aller_a(self, etat: str) -> None:
        if etat not in TRANSITIONS[self.etat]:
            raise ValueError(f"transition interdite : {self.etat} → {etat}")
        self.etat = etat
        self.historique.append(etat)

    def ajouter_message(self, msg: dict) -> None:
        self.messages.append(msg)

    def ajouter_artefact(self, nom: str, texte: str) -> None:
        self.artefacts.append({"nom": nom, "parts": [{"type": "text", "texte": texte}]})


# ---------------------------------------------------------------- édition par diff : remplacement à occurrence unique
class ErreurEdition(Exception):
    pass


def remplacer(contenu: str, ancien: str, nouveau: str) -> str:
    """Remplace `ancien` par `nouveau` SEULEMENT s'il apparaît exactement une fois : l'édition est alors déterministe."""
    if ancien == "":
        raise ErreurEdition("le motif à remplacer est vide")
    n = contenu.count(ancien)
    if n == 0:
        raise ErreurEdition("motif introuvable")
    if n > 1:
        raise ErreurEdition(f"motif ambigu : {n} occurrences, ajouter du contexte")
    return contenu.replace(ancien, nouveau)


def remplacer_naif_premier(contenu: str, ancien: str, nouveau: str) -> str:
    """Variante FAUTIVE : remplace la première occurrence sans vérifier l'unicité ; dépend de l'ordre de recherche."""
    return contenu.replace(ancien, nouveau, 1)


def diff_unifie(avant: str, apres: str, nom: str) -> str:
    """Patch au format diff unifié (difflib), déterministe : seules les lignes modifiées et leur contexte."""
    lignes = difflib.unified_diff(avant.splitlines(), apres.splitlines(),
                                  fromfile=f"a/{nom}", tofile=f"b/{nom}", lineterm="")
    return "\n".join(lignes)


def tokens(texte: str) -> int:
    """Heuristique des étapes 4 et 72 : environ un token pour quatre caractères (illustratif)."""
    return round(len(texte) / 4)


def economie_tokens(fichier: str, patch: str) -> int:
    """Tokens de sortie économisés par un patch plutôt qu'une réécriture complète : tokens(fichier) − tokens(patch)."""
    return tokens(fichier) - tokens(patch)


# ---------------------------------------------------------------- l'agent éditeur (le serveur A2A, en mémoire)
CARTE_EDITEUR = CarteAgent(
    nom="agent-editeur-documents",
    description="Édite un document texte par remplacement ciblé et renvoie le diff unifié.",
    version="0.1.0",
    competences=[Competence("editer_document", "Éditer un document",
                            "Remplace un passage unique par un autre et renvoie le patch.")],
)


class AgentEditeur:
    """Reçoit une tâche d'édition, l'exécute par `remplacer`, renvoie un artefact = le patch. Tout en mémoire."""

    def __init__(self, documents: dict):
        self.documents = documents
        self.carte = CARTE_EDITEUR

    def traiter(self, tache: Tache, instruction: dict) -> None:
        tache.aller_a(EN_COURS)
        nom = instruction["document"]
        avant = self.documents[nom]
        try:
            apres = remplacer(avant, instruction["ancien"], instruction["nouveau"])
        except ErreurEdition as e:
            if "introuvable" in str(e):
                tache.ajouter_message(message("agent", f"texte introuvable dans {nom} ; donnez le passage exact"))
                tache.aller_a(ENTREE_REQUISE)
            else:
                tache.ajouter_message(message("agent", f"édition refusée : {e}"))
                tache.aller_a(ECHOUEE)
            return
        self.documents[nom] = apres
        patch = diff_unifie(avant, apres, nom)
        tache.ajouter_artefact(f"{nom}.patch", patch)
        tache.ajouter_message(message("agent", f"édition appliquée ; {economie_tokens(apres, patch)} tokens de sortie économisés"))
        tache.aller_a(TERMINEE)


# ---------------------------------------------------------------- l'agent orchestrateur (le client A2A)
class AgentOrchestrateur:
    """Découvre l'agent distant par sa carte, vérifie la compétence, envoie des tâches et lit les artefacts."""

    def __init__(self, distant: AgentEditeur):
        self.distant = distant
        self.prochain_id = 1

    def decouvrir(self, competence_id: str) -> Competence:
        carte = json.loads(self.distant.carte.json())    # la carte voyage en JSON, puis est relue par le client
        trouvee = next((c for c in carte["competences"] if c["id"] == competence_id), None)
        if trouvee is None:
            raise RuntimeError(f"l'agent distant n'a pas la compétence {competence_id}")
        return Competence(**trouvee)

    def confier(self, instruction: dict) -> Tache:
        tache = Tache(f"t{self.prochain_id}", message("user", json.dumps(instruction, ensure_ascii=False, sort_keys=True)))
        self.prochain_id += 1
        self.distant.traiter(tache, instruction)
        return tache


DOCUMENTS = {
    "config_bail": "\n".join(
        [f"clause_{i:02d} = valeur_{i:02d}" for i in range(1, 31)]),
    "fiche_locataire": ("locataire = Fatima\nmontant_aed = 90000\npaiements = 4\n"
                        "depot_aed = 90000\nemirat = Dubai"),
}


def main() -> None:
    print("1. Découverte : l'orchestrateur lit la carte de l'agent éditeur (JSON)")
    editeur = AgentEditeur(dict(DOCUMENTS))
    orch = AgentOrchestrateur(editeur)
    comp = orch.decouvrir("editer_document")
    print(f"  carte : {editeur.carte.nom} v{editeur.carte.version} ; compétence trouvée : {comp.id}")
    assert comp.id == "editer_document"
    try:
        orch.decouvrir("virer_des_fonds")
    except RuntimeError as e:
        print(f"  compétence absente → {e}")

    print("2. Tâche valide : une édition à occurrence unique sur un document de 30 lignes")
    t1 = orch.confier({"document": "config_bail", "ancien": "clause_15 = valeur_15", "nouveau": "clause_15 = 999"})
    patch = t1.artefacts[0]["parts"][0]["texte"]
    print(f"  état : {' → '.join(t1.historique)} ; artefact : {t1.artefacts[0]['nom']}")
    for ligne in patch.splitlines():
        print(f"    {ligne}")
    assert t1.historique == [SOUMISE, EN_COURS, TERMINEE]
    assert "clause_15 = valeur_15" in patch and "clause_15 = 999" in patch
    assert editeur.documents["config_bail"].count("clause_15 = 999") == 1

    print("3. Économie de tokens : le patch contre la réécriture complète")
    apres = editeur.documents["config_bail"]
    eco = economie_tokens(apres, patch)
    print(f"  fichier {len(apres)} caractères (~{tokens(apres)} tokens), patch {len(patch)} caractères "
          f"(~{tokens(patch)} tokens) → {eco} tokens économisés")
    assert tokens(apres) == 163 and tokens(patch) == 58 and eco == 105

    print("4. Occurrence unique = édition déterministe ; sinon, ambiguïté refusée")
    fiche = editeur.documents["fiche_locataire"]
    t2 = orch.confier({"document": "fiche_locataire", "ancien": "90000", "nouveau": "95000"})
    print(f"  « 90000 » apparaît {fiche.count('90000')} fois → état {t2.etat} : {t2.messages[-1]['parts'][0]['texte']}")
    assert t2.historique == [SOUMISE, EN_COURS, ECHOUEE] and editeur.documents["fiche_locataire"] == fiche
    naif = remplacer_naif_premier(fiche, "90000", "95000")
    print(f"  variante fautive « premier » : montant={naif.count('montant_aed = 95000')}, depot={naif.count('depot_aed = 95000')} (une seule ligne changée, la mauvaise peut l'être)")
    assert naif != remplacer_naif_premier(fiche[::-1], "90000"[::-1], "95000"[::-1])[::-1]  # dépend du sens de lecture
    t3 = orch.confier({"document": "fiche_locataire", "ancien": "depot_aed = 90000", "nouveau": "depot_aed = 95000"})
    print(f"  avec le contexte de la ligne → état {t3.etat} ; depot_aed = 95000 : {editeur.documents['fiche_locataire'].count('depot_aed = 95000')}")
    assert t3.historique == [SOUMISE, EN_COURS, TERMINEE]
    assert editeur.documents["fiche_locataire"].count("montant_aed = 90000") == 1   # le montant n'a pas bougé

    print("5. Tâche dont le texte est introuvable : l'agent demande une précision (cycle de vie)")
    t4 = orch.confier({"document": "fiche_locataire", "ancien": "iban = AE00", "nouveau": "iban = AE07"})
    print(f"  état : {' → '.join(t4.historique)} ; message : {t4.messages[-1]['parts'][0]['texte']}")
    assert t4.historique == [SOUMISE, EN_COURS, ENTREE_REQUISE]
    try:
        t4.aller_a(TERMINEE)                       # ENTREE_REQUISE → TERMINEE n'est pas permis
    except ValueError as e:
        print(f"  transition refusée : {e}")
    assert t4.etat == ENTREE_REQUISE
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Découverte : l'orchestrateur lit la carte de l'agent éditeur (JSON)
  carte : agent-editeur-documents v0.1.0 ; compétence trouvée : editer_document
  compétence absente → l'agent distant n'a pas la compétence virer_des_fonds
2. Tâche valide : une édition à occurrence unique sur un document de 30 lignes
  état : soumise → en-cours → terminée ; artefact : config_bail.patch
    --- a/config_bail
    +++ b/config_bail
    @@ -12,7 +12,7 @@
    -clause_15 = valeur_15
    +clause_15 = 999
…
3. Économie de tokens : le patch contre la réécriture complète
  fichier 653 caractères (~163 tokens), patch 231 caractères (~58 tokens) → 105 tokens économisés
4. Occurrence unique = édition déterministe ; sinon, ambiguïté refusée
  « 90000 » apparaît 2 fois → état échouée : édition refusée : motif ambigu : 2 occurrences, ajouter du contexte
  variante fautive « premier » : montant=1, depot=0 (une seule ligne changée, la mauvaise peut l'être)
  avec le contexte de la ligne → état terminée ; depot_aed = 95000 : 1
5. Tâche dont le texte est introuvable : l'agent demande une précision (cycle de vie)
  état : soumise → en-cours → entrée-requise ; message : texte introuvable dans fiche_locataire ; donnez le passage exact
  transition refusée : transition interdite : entrée-requise → terminée
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : déléguer à un agent, c'est lui confier une tâche qui a un état et un historique, pas lancer un appel qui rend aussitôt une valeur ; et éditer un document, c'est remplacer un passage **unique** et renvoyer un **patch**, jamais réécrire le tout.

## Formule naturelle : déterminisme et tokens économisés

Deux résultats chiffrent l'édition par diff. Le premier porte sur la **sûreté** : une occurrence unique rend l'édition déterministe. Le second sur le **coût** : le patch économise des tokens de sortie en proportion de la taille du fichier.

$$
c = \text{nombre d'occurrences de } a \text{ dans } F
$$

$$
c = 1 \;\Longrightarrow\; \text{remplacer}(F, a, b) \text{ a un résultat unique}
$$

$$
\text{tokens}(x) \approx \frac{|x|}{4}
$$

$$
E = \text{tokens}(F) - \text{tokens}(P) \approx \frac{|F| - |P|}{4}
$$

### Décryptage des symboles

$$
F
$$

Le contenu du fichier avant édition, une chaîne de caractères ; argument `contenu` de `remplacer`, et `avant` de `diff_unifie`.

$$
a,\quad b
$$

Le passage à remplacer et son remplaçant ; arguments `ancien` et `nouveau`. Le symbole a joue ici le rôle d'un motif de recherche, non d'un poids.

$$
c
$$

Le nombre d'occurrences de a dans F, un entier ≥ 0 ; `contenu.count(ancien)`. L'édition n'est permise que si c = 1.

$$
P
$$

Le patch, c'est-à-dire le diff unifié entre F et le fichier édité ; valeur renvoyée par `diff_unifie`, rangée comme artefact de la tâche.

$$
|x|
$$

La longueur en caractères d'une chaîne x ; `len(x)` en Python.

$$
E
$$

Les tokens de sortie économisés en émettant le patch plutôt que le fichier réécrit, un entier qui peut être négatif pour un très petit fichier ; `economie_tokens(fichier, patch)`.

## Démonstration

### 1. Une occurrence unique rend l'édition déterministe

L'ensemble des positions où a apparaît dans F est un ensemble fini de départs i tels que le tronçon de F qui commence en i et a la longueur de a est égal à a. Appliquer l'édition, c'est choisir une de ces positions et y substituer b. Quand c = 1, cet ensemble est un singleton : il n'y a **qu'une seule** position possible, donc une seule façon d'appliquer l'édition, et le résultat ne dépend ni de l'ordre de recherche, ni de l'implémentation. L'édition est déterministe, ce qui est la propriété qu'on veut pour un agent : la même instruction produit toujours le même document.

Quand c ≥ 2, le choix n'est plus forcé. Une stratégie « remplacer la première occurrence » et une stratégie « remplacer la dernière » donnent des documents différents. Le programme le montre sur la fiche locataire, où « 90000 » est à la fois le montant et le dépôt. La variante naïve qui change la première occurrence modifie la ligne `montant_aed`, tandis que la même variante appliquée au texte lu à l'envers modifie la ligne `depot_aed` : deux résultats incompatibles pour la même intention « passer 90000 à 95000 ». Pire, si l'utilisateur voulait changer le dépôt, la variante « première occurrence » change le montant — la mauvaise ligne. C'est pourquoi `remplacer` **refuse** le cas ambigu et réclame du contexte : « depot_aed = 90000 » n'apparaît qu'une fois, et devient le motif sûr. Après cette édition, le montant n'a pas bougé, ce que vérifie le programme.

### 2. Zéro occurrence : refuser plutôt que deviner

Si c = 0, le passage n'existe pas. Un outil qui, dans ce cas, ne ferait rien en silence laisserait l'agent croire son édition faite ; un outil qui insérerait le texte ailleurs inventerait une modification. `remplacer` lève une erreur, et l'agent éditeur fait passer la tâche à « entrée requise » en demandant le passage exact. Le cycle de vie exprime ainsi une vérité : la tâche n'est ni réussie ni échouée, elle attend une précision. La transition directe de « entrée requise » vers « terminée » est refusée par la machine à états, parce qu'il faut repasser par « en cours » pour retravailler.

### 3. Le patch économise des tokens de sortie en proportion de la taille du fichier

Réécrire le fichier coûte en sortie tokens(F) ; émettre le patch coûte tokens(P). L'économie est leur différence. Avec l'heuristique « un token pour quatre caractères » des étapes 4 et 72, elle vaut à peu près (|F| − |P|) / 4. Sur le document de 30 lignes du programme, |F| = 653 caractères, soit environ 163 tokens, et le patch fait |P| = 231 caractères, soit environ 58 tokens : l'économie est de 105 tokens de sortie, pour une édition d'une seule ligne.

Le gain croît avec la taille du fichier, parce que le patch ne dépend que de l'étendue de la modification et de ses lignes de contexte, pas de la longueur totale du fichier. Pour une édition locale d'un fichier de K lignes, tokens(P) reste à peu près constant quand K grandit, tandis que tokens(F) croît avec K : l'économie E ≈ tokens(F) − constante augmente donc linéairement avec K. Ce raisonnement a une limite, qu'il faut dire : pour un très petit fichier, le patch, avec son en-tête et ses lignes de contexte, peut être **plus long** que le fichier lui-même, et E devient négatif. On réécrit alors directement. Le diff gagne sur les fichiers longs modifiés par petites touches, exactement le cas d'un agent qui corrige un contrat ou une configuration.

### 4. Exemple fait à la main (le code reprend ces nombres)

| Grandeur | Calcul | Résultat |
|---|---|---|
| occurrences de « clause_15 = valeur_15 » | comptage | 1 (édition permise) |
| occurrences de « 90000 » dans la fiche | comptage | 2 (édition refusée) |
| tokens du fichier de 30 lignes | round(653 / 4) | 163 |
| tokens du patch | round(231 / 4) | 58 |
| tokens économisés | 163 − 58 | 105 |
| cycle d'une tâche réussie | soumise → en-cours → terminée | 3 états |
| cycle d'une tâche ambiguë | soumise → en-cours → échouée | 3 états |

## Squelette algorithmique

Le fichier contient deux algorithmes principaux : traiter une tâche A2A d'édition en suivant le cycle de vie, et appliquer un remplacement sûr à occurrence unique. Dans les complexités, L désigne la longueur du document en caractères et M la longueur du motif.

### Traiter une tâche d'édition (A2A)

Entrées : une tâche, une instruction (document, ancien, nouveau). Sortie : la tâche, dont l'état devient terminée, échouée ou entrée requise, avec un artefact si elle réussit. Idée : passer en cours, tenter l'édition sûre, et choisir l'état final selon la cause de l'échec.

```text
ALGORITHME TraiterTâche
ENTRÉES : tâche t (état SOUMISE) ; instruction (document d, ancien a, nouveau b)
SORTIE  : t avec un état final ou « entrée requise », et un artefact si succès
  t.aller_à(EN_COURS)
  avant ← documents[d]
  ESSAYER après ← Remplacer(avant, a, b)
  SI échec « introuvable » ALORS
    ajouter un message « donnez le passage exact » ; t.aller_à(ENTREE_REQUISE) ; RETOURNER
  SINON SI échec « ambigu » ALORS
    ajouter un message « édition refusée » ; t.aller_à(ECHOUEE) ; RETOURNER
  FIN SI
  documents[d] ← après
  patch ← DiffUnifié(avant, après, d)
  ajouter l'artefact patch ; t.aller_à(TERMINEE)

ALGORITHME AllerÀ(t, e)                       ▷ garde de la machine à états
  SI e ∉ TRANSITIONS[t.état] ALORS ERREUR « transition interdite » FIN SI
  t.état ← e ; empiler e dans l'historique
```

**Complexité :** O(L) en temps, dominé par le comptage des occurrences et le calcul du diff, tous deux linéaires en la longueur du document ; la gestion d'état est en O(1). En mémoire, O(L) pour le document édité et le patch.

**Du squelette au code :** `TraiterTâche` est `AgentEditeur.traiter`, avec le `try/except ErreurEdition` qui aiguille vers `ENTREE_REQUISE` ou `ECHOUEE` selon le message ; `AllerÀ` est `Tache.aller_a`, dont la garde lit `TRANSITIONS[self.etat]`.

### Remplacement à occurrence unique

Entrées : un contenu, un motif, un remplaçant. Sortie : le contenu édité, ou une erreur. Idée : ne modifier que si le motif est présent une seule fois, pour garantir le déterminisme.

```text
ALGORITHME Remplacer
ENTRÉES : contenu F ; motif a ; remplaçant b
SORTIE  : F édité, ou ERREUR
  SI a est vide ALORS ERREUR « motif vide » FIN SI
  c ← nombre d'occurrences de a dans F
  SI c = 0 ALORS ERREUR « introuvable » FIN SI
  SI c > 1 ALORS ERREUR « ambigu : c occurrences » FIN SI
  RETOURNER F où l'unique occurrence de a est remplacée par b
```

**Complexité :** O(L) en temps pour compter puis remplacer, avec une passe de recherche de motif de longueur M sur un texte de longueur L ; O(L) en mémoire pour la copie éditée. Le comptage préalable est ce qui coûte une passe de plus qu'un remplacement naïf, et c'est le prix du déterminisme.

**Du squelette au code :** c'est `remplacer(contenu, ancien, nouveau)`, avec `contenu.count(ancien)` pour c et `contenu.replace(ancien, nouveau)` pour l'unique substitution ; `remplacer_naif_premier` est la version sans garde, gardée pour le contre-exemple.

## Cas d'usage réels aux Émirats

Les compétences, délais et volumes ci-dessous sont illustratifs ; les règles citées sont à confirmer avec le texte en vigueur.

### Immobilier — un orchestrateur qui délègue la rédaction d'un avenant

Une agence et un promoteur de Dubaï et d'Abu Dhabi font travailler ensemble deux agents : un orchestrateur qui dialogue avec le conseiller, et un agent rédacteur spécialisé dans les contrats Ejari. Quand le conseiller demande de porter le loyer d'un bail de 90 000 à 95 000 AED, l'orchestrateur découvre la compétence `editer_document` de l'agent rédacteur par sa carte, puis lui confie une tâche A2A. Le rédacteur édite par diff : il remplace la ligne du loyer, pas le montant « 90000 » nu qui apparaît aussi comme dépôt, et renvoie un patch que le conseiller relit avant signature. Sans l'occurrence unique, l'agent risquait de changer le dépôt au lieu du loyer (démonstration, point 1) ; sans A2A, l'orchestrateur devait embarquer toute la logique de rédaction. Un document juridique généré n'a de valeur qu'après relecture humaine, comme le rappelle l'étape 47. On suit la part des avenants corrigés en relecture et le nombre d'éditions refusées pour ambiguïté.

### Banque — une délégation entre équipes, pas un simple appel d'outil

Une banque de détail de Dubaï sépare un agent de front, tenu par l'équipe service client, et un agent de conformité, tenu par une autre équipe. Quand une demande touche un dossier sensible, l'agent de front **délègue** à l'agent de conformité par A2A : il confie une tâche, et attend un verdict qui peut passer par « entrée requise » si une pièce manque. C'est exactement le cas où MCP ne suffit pas : l'agent de conformité n'est pas un outil qui rend une valeur, c'est un agent qui raisonne et peut redemander. La disponibilité de cet agent se mesure comme celle d'un serveur MCP (étape 49), et sa tâche peut elle-même appeler des outils MCP de lecture. Sans frontière entre les deux agents, un seul programme cumulerait deux responsabilités réglementaires distinctes. On suit le délai de traitement des tâches déléguées et la part de celles qui repassent par « entrée requise ».

### BTP — éditer un devis long sans le réécrire

Un groupe de construction qui mène de grands chantiers à Dubaï fait tenir ses devis, longs de plusieurs centaines de lignes, par un agent. Quand un poste change — une quantité de béton, un prix unitaire —, l'agent n'émet pas le devis entier mais un patch, par édition à occurrence unique sur la ligne concernée. Sur un devis de plusieurs milliers de caractères, le patch en fait quelques centaines : l'économie de tokens de sortie se chiffre en milliers (démonstration, point 3), et le coût de sortie, qui ne baisse ni par le cache ni par la fenêtre (étape 72), diminue d'autant. Surtout, le reste du devis ne peut pas être altéré par mégarde, puisque le patch ne touche que la ligne visée. La TVA de 5 % et la retenue de garantie sont recalculées par un outil, et le nouveau total figure dans le patch. On suit le nombre moyen de tokens de sortie par modification et le taux de patches appliqués sans conflit.

### RH — un agent rédacteur de lettres, piloté par un orchestrateur

Un cabinet RH multi-émirats confie à un agent spécialisé la rédaction des lettres administratives (attestation de salaire, certificat de travail), piloté par un orchestrateur qui connaît le dossier du salarié. L'orchestrateur découvre la carte du rédacteur, vérifie qu'il a la compétence voulue, puis lui confie une tâche en lui passant les champs nécessaires et rien de plus, par souci de minimisation des données (PDPL). Le rédacteur modifie un modèle de lettre par diff — le nom, la date, le montant de l'indemnité de fin de service calculée par l'outil canonique (55 000 AED pour 10 000 AED de base et sept ans) — et renvoie le patch. Si un champ manque dans le modèle, la tâche passe en « entrée requise » plutôt que d'inventer une valeur. Sans ce cycle de vie, un champ absent produirait une lettre fausse ou un blocage silencieux. On suit la part des lettres générées sans retouche et le nombre de tâches en attente d'une précision.

### Secteur public — une carte d'agent qui déclare un périmètre strict

Une entité de services publics en ligne, accessible par UAE Pass, expose un agent dont la carte ne déclare qu'une compétence : éditer les brouillons de démarches de l'usager connecté. Un agent tiers qui voudrait lui faire « virer des fonds » ou « lire un autre dossier » ne trouve pas la compétence dans la carte et reçoit un refus, exactement comme l'orchestrateur du programme face à `virer_des_fonds`. La carte joue ainsi le même rôle qu'un catalogue de capacités : ce qui n'y est pas déclaré n'existe pas pour l'autre côté. Les noms d'états de la tâche, génériques ici, sont à aligner sur la spécification publiée au moment de l'intégration. Sans cette déclaration explicite, un agent distant pourrait supposer des capacités que l'agent n'a pas. On suit le nombre de compétences demandées et introuvables, indicateur d'un agent tiers mal configuré ou malveillant.

### Assurance — un patch comme trace vérifiable d'une correction

Un assureur auto et santé, supervisé par la CBUAE, fait corriger par un agent les fiches de sinistre qui contiennent une erreur de saisie. Chaque correction passe par l'édition à occurrence unique : l'agent remplace le passage exact, et le patch produit est archivé comme **trace** de ce qui a changé, qui et quand. Un diff unifié est lisible par un humain et rejouable par `patch` : l'auditeur voit la ligne avant et après, sans avoir à comparer deux versions entières du document. L'occurrence unique garantit qu'aucune autre partie de la fiche n'a bougé, ce qui est exactement ce qu'un contrôle veut pouvoir affirmer. Sans patch, une correction serait une réécriture opaque, difficile à auditer. On suit le nombre de corrections dont le patch a été appliqué proprement et la taille moyenne des patches, dont une hausse signalerait des réécritures trop larges.

## Pièges et limites

- **Remplacer une occurrence parmi plusieurs.** Un `replace` naïf dépend de l'ordre et peut changer la mauvaise ligne (démonstration, point 1). On exige l'occurrence unique et l'on ajoute du contexte sinon.
- **Prendre A2A pour MCP, ou l'inverse.** A2A relie deux agents qui raisonnent ; MCP relie un agent à ses outils. Une tâche A2A peut passer par « entrée requise » ; un `tools/call` rend une valeur.
- **Croire les noms d'états figés.** Les états et les champs retenus ici sont génériques ; selon la spécification publiée, à vérifier pour les noms exacts avant toute intégration réelle.
- **Émettre un patch sur un fichier minuscule.** Le diff, avec son en-tête et son contexte, peut être plus long que le fichier (point 3). On réécrit directement les très petits fichiers.
- **Oublier que la carte est publique.** La carte d'agent déclare des capacités à des tiers ; sa description est lue par d'autres agents comme une consigne, et doit être traitée comme du texte non fiable à l'arrivée (étape 66).

### Exercice feuille blanche

1. Sans regarder le code, écrire `remplacer(contenu, ancien, nouveau)` avec ses trois cas (vide, introuvable, ambigu, unique), puis vérifier qu'un motif présent deux fois lève une erreur.
2. Prédire, puis vérifier : sur la fiche locataire, `remplacer(fiche, "paiements = 4", "paiements = 12")` réussit-il ? Combien d'occurrences ? (Réponse : oui, une seule occurrence, édition déterministe.)
3. Trouver le bug : une variante de `aller_a` ne vérifie pas `TRANSITIONS` et change l'état sans garde. Quel `assert` de la section 5 échoue ? (Réponse : `t4.etat == ENTREE_REQUISE`, puisque la transition vers « terminée » passerait sans être refusée.)
4. Calculer à la main : un fichier de 4 000 caractères, un patch de 320 caractères. Combien de tokens de sortie économisés par l'heuristique « un token pour quatre caractères » ? (Réponse : (4000 − 320) / 4 = 920 tokens.)

## Pour aller plus loin

En production, A2A s'appuie sur un transport réseau (HTTP, avec notifications d'avancement pour les tâches longues) plutôt que sur l'échange en mémoire de ce fichier, et l'authentification y relie une tâche à l'identité de l'agent appelant. L'édition par diff se généralise à plusieurs remplacements dans une même tâche, chacun à occurrence unique, et à l'application d'un patch par `patch` ou par une bibliothèque de fusion à trois points quand le fichier a changé entre-temps. Pour du code, les mêmes principes valent : un agent qui modifie un dépôt émet des patches ciblés, relus et testés, jamais une réécriture complète de chaque fichier.

> Suite : [Précision, rappel, F1 et KL](<../10-Evaluation/50-Precision-Rappel-F1-et-KL.md>) — étape 50.
