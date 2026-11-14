# Étape 7 — Passer au vrai LLM

> Palier 12 · Étape 7 sur 8 · Précédent : [Étape 6 — Les variantes et la barrière CI](<06-Variantes-et-barriere-CI.md>) · Suivant : [Étape 8 — Assembler, lancer et récapituler les douze paliers](<08-Assembler-lancer-et-recapituler.md>) · Énoncé : [README du palier 12](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Tout ce que tu as écrit depuis le palier 01 parle à un **port** : un objet qui a une méthode `create(system=…, messages=…, tools=…)` et qui rend une réponse portant `stop_reason` et `content`, une liste de blocs ayant `type`, `text`, `id`, `name` et `input`. Ce n'est pas un hasard : c'est exactement la forme des réponses de l'API Claude. Passer au vrai modèle ne demande donc qu'un second **adaptateur**, qui implémente le même port en appelant l'API. Rien d'autre ne change : ni la boucle, ni la porte, ni les outils, ni le journal, ni l'évaluation.

En Java, c'est l'architecture hexagonale que tu connais : une interface `ModelePort`, un adaptateur `FakeLLM` actif sous le profil `test` et un adaptateur `ClaudeLLM` actif sous le profil `prod`. L'`Agent` ne connaît que l'interface.

L'adaptateur est fourni complet dans `agent/adaptateur_claude.py`, et il n'est jamais exécuté par les tests : il faut le SDK, une clé et le réseau. Cette étape le lit ligne par ligne, pour que tu saches le réécrire et le modifier sans casser les règles de l'API.

## Pourquoi l'import est dans le constructeur

L'étape 77 importe le SDK en tête de fichier :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.__init__(model, effort)`** — Ce constructeur de l'étape 77 ressemble à un interprète qu'on aurait fait venir au bureau dès l'ouverture, même les jours sans réunion : sa présence est exigée dès qu'on franchit la porte du module. Il reçoit le nom du modèle, `"claude-opus-5-5"` par défaut, et le niveau d'effort, `"medium"`, crée un client `anthropic.Anthropic()` à partir du SDK importé en tête de fichier, et range le modèle et l'effort dans l'instance, sans rien rendre. Il marche dans un fichier isolé, mais dans un paquet, le simple fait d'importer le module échouerait par `ModuleNotFoundError` sur une machine sans le SDK, et le plafond de tokens reste écrit en dur ailleurs.

```python
# [extrait] brouillon
import anthropic                                   # en tête de module : tout le paquet dépend du SDK


class ClaudeLLM:
    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.effort = effort
```

Dans un fichier isolé, que le harnais du cours ne fait que lire, c'est sans conséquence. Dans un paquet, c'est un piège : tout module qui importerait `agent.adaptateur_claude`, ne serait-ce que pour vérifier que les noms existent, échouerait par `ModuleNotFoundError` sur une machine sans le SDK, par exemple la machine d'intégration continue qui fait tourner les 165 tests en bibliothèque standard. La version du paquet déplace l'import **dans** le constructeur, et ajoute un paramètre `max_tokens` au lieu de laisser 16000 en dur dans l'appel.

## La classe et son constructeur

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.__init__(model, effort, max_tokens)`** — Le constructeur du paquet est l'interprète qu'on ne convoque qu'au moment où l'on en a besoin : tant qu'on n'a pas construit d'adaptateur, personne ne lui demande de venir. Il reçoit le nom du modèle, `"claude-opus-5-5"`, le niveau d'effort, `"medium"`, et le plafond de tokens de chaque réponse, 16000, tous avec une valeur par défaut si bien que `ClaudeLLM()` suffit. Il importe `anthropic` à l'intérieur de son propre corps, crée un client qui cherche lui-même la clé dans `ANTHROPIC_API_KEY` ou dans le profil de `ant auth login`, puis range les trois réglages dans des attributs publics ; il ne rend rien et n'envoie aucune requête, et une installation manquante du SDK ne se révèle qu'à cette construction, jamais à l'import du module.

```python
# [extrait] agent/adaptateur_claude.py
class ClaudeLLM:
    """Même interface que FakeLLM : `create(system=…, messages=…, tools=…)` rend une réponse qui a
    `.stop_reason` et `.content` (blocs `.type`, `.text`, `.id`, `.name`, `.input`).

    `fallbacks="default"` (bêta `server-side-fallback-2026-07-01`) : si le modèle principal refuse une
    requête, l'API la rejoue elle-même sur un modèle de repli choisi selon la catégorie du refus.
    Retirer ces deux paramètres pour que chaque refus arrête la boucle avec le statut « refus ».
    """

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium", max_tokens: int = 16000) -> None:
        import anthropic                      # import local : le paquet ne dépend pas du SDK

        self.client = anthropic.Anthropic()   # lit ANTHROPIC_API_KEY ou le profil créé par `ant auth login`
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
```

**La docstring de la classe** énonce le contrat du port, le même que celui de `FakeLLM`, et documente le seul comportement qui n'existe pas dans le faux modèle : le repli automatique en cas de refus, et comment le désactiver.

**La signature.** Trois paramètres, tous avec une valeur par défaut, si bien que `ClaudeLLM()` suffit. `model="claude-opus-5-5"` désigne Claude Opus 5.5. `effort="medium"` est le niveau d'effort, qui règle la profondeur de la réflexion et la dépense de tokens ; c'est la valeur par défaut de ce modèle, écrite ici explicitement pour qu'on la voie et qu'on la change en connaissance de cause. `max_tokens=16000` plafonne la longueur de chaque réponse.

**L'import local.** `import anthropic` ne s'exécute que lorsqu'on **construit** un `ClaudeLLM`. Importer le module, ou lancer les tests, ne demande ni le SDK ni le réseau. C'est l'équivalent d'une dépendance Maven en portée `provided`, chargée seulement par le profil qui l'utilise. Le prix à payer est qu'une erreur d'installation n'apparaît qu'à la construction : on la voit en démarrant l'agent de production, pas en important le paquet.

**Le client.** `anthropic.Anthropic()` sans argument cherche lui-même ses identifiants : la variable d'environnement `ANTHROPIC_API_KEY`, ou le profil créé par la commande `ant auth login`. La clé n'apparaît donc jamais dans le code, ni dans le journal. Le client relance aussi de lui-même, deux fois par défaut, les erreurs passagères (limite de débit, surcharge, coupure réseau) : c'est la même idée que l'`executer_avec_relances` du palier 11, logée dans le SDK.

**Les trois attributs** gardent les réglages pour `create`. Ils sont publics : un test ou un script d'expérience peut lire `llm.effort`, ou en construire un second avec un autre niveau pour comparer.

## La méthode create

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`ClaudeLLM.create(system, messages, tools)`** — Cette méthode est le guichet unique du port LLM, où la boucle dépose sa question et reprend la réponse, sans savoir si derrière la vitre se tient un acteur de répétition ou le vrai modèle. Elle reçoit, uniquement par mots-clés grâce à l'étoile de sa signature, le prompt système, l'historique et les définitions d'outils strictes, et envoie un appel à `self.client.beta.messages.create` avec le modèle, `max_tokens`, l'effort rangé dans `output_config`, la bêta `server-side-fallback-2026-07-01` et `fallbacks="default"`. Si la réponse s'arrête sur `"refusal"` et porte des `stop_details`, elle imprime leur catégorie et leur explication ; elle rend ensuite la réponse de l'API telle quelle, avec son `stop_reason` et son `content`, sans conversion ni copie, et c'est la boucle qui décidera du statut.

```python
# [extrait] agent/adaptateur_claude.py
class ClaudeLLM:
    ...
    def create(self, *, system: str, messages: list, tools: list):
        """Un appel à l'API ; la réflexion adaptative est active par défaut sur ce modèle."""
        reponse = self.client.beta.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            tools=tools,                             # [{"name", "description", "input_schema", "strict": True}]
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if reponse.stop_reason == "refusal" and reponse.stop_details:
            print(f"refus : {reponse.stop_details.category} — {reponse.stop_details.explanation}")
        return reponse
```

**La signature** est celle de `FakeLLM.create`, au caractère près. L'étoile `*` oblige l'appelant à nommer les trois arguments : `executer_agent` écrit `llm.create(system=system, messages=messages, tools=schemas)`, et un appel positionnel, qui pourrait inverser deux arguments sans erreur, est refusé.

**`self.client.beta.messages.create(...)`** envoie une requête à l'API Messages. On passe par l'espace `beta` du SDK parce que la requête active une fonctionnalité en bêta, les replis en cas de refus. Les paramètres, un par un :

- `model` et `max_tokens` : le modèle et le plafond de la réponse. Si le modèle atteint le plafond, la réponse s'arrête avec `stop_reason` égal à "max_tokens", que la boucle traduit en statut « tronque ».
- `system` et `messages` : le prompt système et l'historique, construits par `construire_prompt` et `executer_agent`, transmis sans retouche. L'adaptateur n'ajoute rien au prompt : toute la logique de prompt reste dans le domaine.
- `tools` : les définitions rendues par `Registre.definitions_api()`, avec `"strict": True`. En mode strict, l'API garantit que les arguments d'un bloc `tool_use` respectent exactement le schéma. Le mode strict refuse les bornes (`minimum`, `maximum`…) dans le schéma : `definitions_api` les a retirées et recopiées dans les descriptions, et la porte locale du palier 04 continue de les vérifier. Le commentaire rappelle la forme d'une définition.
- `output_config={"effort": self.effort}` : le niveau d'effort, rangé dans `output_config`. Sur ce modèle, la réflexion adaptative est active par défaut : le modèle décide lui-même quand et combien réfléchir, et l'effort règle jusqu'où.
- `betas=["server-side-fallback-2026-07-01"]` et `fallbacks="default"` : la bêta des replis côté serveur, et son mode par défaut. Si le modèle principal refuse la requête, l'API la rejoue elle-même sur un modèle de repli choisi selon la catégorie du refus, sans liste de modèles à maintenir. Pour qu'un refus arrête la boucle avec le statut « refus », on retire ces deux paramètres ensemble.

**Le refus.** `stop_details` n'est renseigné que lorsque `stop_reason` vaut "refusal" ; il porte la catégorie du refus et une explication. Le test `and reponse.stop_details` protège la lecture : on n'accède à `.category` que si l'objet existe. L'adaptateur se contente d'afficher le motif ; c'est la boucle qui décide, en rendant le statut « refus » **avant** de lire le contenu.

**Le retour.** La réponse de l'API est rendue telle quelle : elle a déjà `stop_reason` et `content`, et ses blocs ont `type`, `text`, `id`, `name` et `input`. Pas de conversion, pas de copie : c'est ce qui rend l'adaptateur si court.

## Les quatre règles que la boucle respecte déjà

Elles sont dans `executer_agent` depuis le palier 05, et il faut les connaître pour ne pas les casser en modifiant la boucle.

1. **Pas de `tool_choice` forcé.** Ce modèle refuse qu'on lui impose un outil précis. On laisse le choix automatique, on nomme l'outil attendu dans le prompt, et l'on déclare les outils en mode strict.
2. **Tous les `tool_result` d'une étape dans un seul message `user`.** Dans le scénario (a), les résultats du ratio et de la conversion repartent ensemble. Les répartir sur deux messages apprendrait au modèle à ne plus demander d'outils en parallèle.
3. **`reponse.content` recopié tel quel dans l'historique**, blocs de réflexion compris : le modèle en a besoin pour poursuivre son raisonnement au tour suivant. La boucle ne lit que les blocs `text` et `tool_use`, mais elle renvoie tout.
4. **Un `stop_reason` égal à "refusal" traité avant de lire le contenu.** La boucle s'arrête avec le statut « refus », et ne cherche aucun outil à exécuter dans une réponse refusée.

## Rejouer le scénario (a) avec le vrai modèle

Une fois le SDK installé (`python -m pip install anthropic`) et l'authentification faite (`ant auth login`, ou la variable `ANTHROPIC_API_KEY`), on peut rejouer le scénario du crédit et mesurer le vrai modèle avec les métriques du palier 10 :

```python
# [extrait] brouillon
from agent.adaptateur_claude import ClaudeLLM
from agent.assemblage import A_CONVERSION, A_MENSUALITE, A_RATIO, QUESTION_CREDIT, Agent, memoire_client
from agent.evaluation import tool_call_f1

agent = Agent(ClaudeLLM(), memoire=memoire_client())
res = agent.repondre(QUESTION_CREDIT)
reels = [(nom, args) for nom, args, _ in res["trace"]]
attendus = [("mensualite", A_MENSUALITE), ("ratio_endettement", A_RATIO), ("convertir_aed_usd", A_CONVERSION)]
print(res["statut"], res.get("reponse"), tool_call_f1(attendus, reels))
```

Ce bloc est marqué « brouillon » parce qu'aucun test ne l'exécute : il appelle l'API, donc il coûte, et sa sortie change d'une exécution à l'autre. La seule ligne différente du scénario scripté est la construction de l'agent. Trois choses à observer. La trace réelle peut différer du script : le modèle peut demander le ratio et la conversion en deux fois, ou arrondir la mensualité autrement dans l'argument `nouvelle` ; la Tool Call F1 le mesure. La fidélité approchée de la réponse se calcule de la même façon, avec `res["sources"]`. Et une seule exécution ne prouve rien : on rejoue chaque cas plusieurs fois et l'on regarde la part des essais réussis (étape 60 du cours), en gardant en tête que chaque essai est facturé (palier 11).

Le scénario (c) est le plus instructif à rejouer : quoi que décide le vrai modèle (appeler l'outil, refuser, demander une confirmation), `agent.virements` doit rester vide, parce que l'approbation humaine est dans l'outil, et non dans le prompt.

## Ce qui passe maintenant

Aucun test ne vise l'adaptateur : il n'est jamais exécuté hors ligne. Vérifie seulement qu'il s'importe sans le SDK, depuis `projet/` :

```text
python -c "from agent.adaptateur_claude import ClaudeLLM; print(ClaudeLLM.__name__)"
```

La commande affiche `ClaudeLLM`, même sur une machine où `anthropic` n'est pas installé.
