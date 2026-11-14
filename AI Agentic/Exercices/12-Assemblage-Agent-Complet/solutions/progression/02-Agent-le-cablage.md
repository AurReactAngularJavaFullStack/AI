# Étape 2 — Le constructeur de l'Agent, ou le câblage

> Palier 12 · Étape 2 sur 8 · Précédent : [Étape 1 — Les constantes et ce qui change depuis 77](<01-Constantes-et-ecarts-avec-77.md>) · Suivant : [Étape 3 — Agent.repondre](<03-Agent-repondre.md>) · Énoncé : [README du palier 12](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Le constructeur fabrique des objets qui dépendent les uns des autres. On les écrit donc dans **l'ordre de leurs dépendances**, comme Spring instancie ses beans : d'abord ceux qui ne dépendent de rien, puis ceux qui ont besoin des premiers. Dresse la liste sur une feuille avant de coder.

- L'horloge ne dépend de rien.
- Le journal a besoin de l'horloge (chaque entrée porte son instant).
- L'approbateur a besoin de l'horloge (il attend 120 s) et du journal (il y note sa décision).
- L'outil de virement a besoin de l'approbateur, du journal et de la liste des virements.
- Le registre a besoin de tous ses outils.
- Les outils protégés ont besoin du registre, de la session et du journal.
- Les définitions envoyées au modèle ont besoin du registre.

Le test `test_sept_outils_stricts_envoyes_au_modele` fixe aussi l'**ordre** des outils : `rechercher_reglementation`, les cinq outils de calcul, puis `initier_virement`. C'est l'ordre de 77, et il compte doublement : le modèle voit les outils dans cet ordre, et une liste d'outils qui change d'ordre d'une requête à l'autre casserait le cache du préfixe (palier 11, étape 72 du cours).

## Une première version, avec trois erreurs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Agent.__init__(llm, memoire, session, horloge)`** — Ce constructeur de brouillon ressemble à un électricien pressé qui branche tous les appartements d'un immeuble sur la même horloge murale et oublie de raccorder le disjoncteur. Il reçoit le port LLM, une mémoire, une session dont la valeur par défaut est la constante `SESSION_CLIENT` elle-même et une horloge par défaut fabriquée une seule fois quand Python lit le `def`. Il range ces objets sans les copier, crée un journal et une liste de virements, enregistre les cinq outils de calcul puis la recherche, et prend `registre.appelables()` comme outils : il ne rend rien, mais tous les agents partagent la même horloge, la recherche arrive au mauvais rang, l'outil de virement manque et aucune politique n'est vérifiée.

```python
# [extrait] brouillon
class Agent:
    def __init__(self, llm, memoire=None, session=SESSION_CLIENT, horloge=Horloge(90 * 86_400)):
        self.llm, self.session, self.memoire, self.horloge = llm, session, memoire or [], horloge
        self.journal = JournalAudit(self.horloge)
        self.virements = []
        self.registre = enregistrer_outils_metier(Registre())
        enregistrer_recherche(self.registre)
        self.outils = self.registre.appelables()
        self.schemas = self.registre.definitions_api()
```

**Les valeurs par défaut sont partagées.** `horloge=Horloge(90 * 86_400)` est évaluée **une seule fois**, quand Python lit le `def` : tous les agents créés sans horloge partagent le même objet, et les 120 secondes du scénario (c) décaleraient l'horloge de tous les agents suivants. C'est le piège le plus célèbre de Python, celui des valeurs par défaut mutables. De même, `self.session = session` garde une référence vers `SESSION_CLIENT` lui-même, et `memoire or []` garde la liste de l'appelant, que l'agent pourrait modifier. **L'ordre des outils est faux** : la recherche passe après les cinq calculs, et le test qui lit les noms dans l'ordre échoue. **La politique est contournée** : `registre.appelables()` rend les portes du palier 04, qui valident le schéma mais ne vérifient pas le rôle ; un client `assistant_public` pourrait calculer une mensualité, et l'outil de virement n'est même pas enregistré.

## La version juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Agent.__init__(llm, memoire, session, horloge)`** — Le constructeur juste est le chef de chantier méthodique qui monte les pièces dans l'ordre de leurs dépendances et donne à chaque appartement son propre compteur. Il reçoit le port LLM, sans le typer pour accepter n'importe quel objet doté de `create`, et trois paramètres qui valent `None` par défaut ; il copie la session reçue, ou `SESSION_CLIENT`, en fabriquant un nouvel ensemble de portées, copie la liste des souvenirs, prend l'horloge reçue ou en crée une au jour 90, soit 7 776 000 s, puis crée le journal et l'approbateur sur cette horloge et une liste de virements vide. Il enregistre la recherche, les cinq calculs et le virement dans un registre neuf, enveloppe ce registre par `proteger` et calcule une fois les définitions strictes ; il ne rend rien et ne fait aucun travail métier, si bien qu'un agent neuf expose sept outils, de `rechercher_reglementation` à `initier_virement`, sans le moindre effet de bord.

```python
# [extrait] agent/assemblage.py
class Agent:
    """L'agent assemblé autour d'un port LLM (FakeLLM en test, ClaudeLLM en production).

    Chaque agent a son horloge, son journal d'audit, son approbateur, son registre de sept outils
    (dans l'ordre de 77) et sa liste `virements` (le « cœur bancaire » simulé). `outils` est le
    dictionnaire protégé : politique, puis schéma, puis outil.
    """

    def __init__(self, llm, memoire: list[Souvenir] | None = None, session: dict | None = None,
                 horloge: Horloge | None = None) -> None:
        s = SESSION_CLIENT if session is None else session
        self.llm = llm
        self.session = {"role": s["role"], "portees": set(s["portees"])}
        self.memoire = list(memoire or [])
        self.horloge = horloge if horloge is not None else Horloge(JOUR_COURANT * 86_400)
        self.journal = JournalAudit(self.horloge)
        self.approbateur = Approbateur(self.horloge, self.journal)
        self.virements: list[dict] = []
        self.registre = enregistrer_recherche(Registre())
        enregistrer_outils_metier(self.registre)
        enregistrer_virement(self.registre, self.approbateur, self.journal, self.virements)
        self.outils = proteger(self.registre, self.session, self.journal)
        self.schemas = self.registre.definitions_api()
```

**La signature.** Quatre paramètres, et seul le premier est obligatoire : le port du modèle. `llm` n'a volontairement **pas** d'annotation de type : l'agent accepte n'importe quel objet qui a une méthode `create(system=…, messages=…, tools=…)`. C'est le typage par le comportement de Python ; en Java, on déclarerait une interface `ModelePort` et `FakeLLM` comme `ClaudeLLM` l'implémenteraient. Les trois autres valent `None` par défaut, et le corps choisit la vraie valeur : c'est la parade au piège des valeurs par défaut partagées.

**La session.** `s` vaut la session reçue, ou `SESSION_CLIENT` si l'appelant n'en donne pas. On écrit `if session is None` et non `session or SESSION_CLIENT`, pour qu'une session explicitement vide reste vide au lieu de devenir silencieusement la session client. Puis on fabrique un **nouveau** dictionnaire, avec un **nouvel** ensemble de portées : `set(s["portees"])` copie l'ensemble. L'agent peut ainsi évoluer sans jamais toucher la constante du module ni la session de l'appelant. C'est une copie défensive, comme `new HashSet<>(portees)` dans un constructeur Java.

**Le modèle et la mémoire.** `self.llm = llm` garde le port tel quel. `list(memoire or [])` copie la liste des souvenirs, ou part d'une liste vide. Attention, c'est une copie **superficielle** : la liste est neuve, mais les objets `Souvenir` sont les mêmes ; quand `rappeler` met à jour leur `jour_acces`, l'appelant le voit. C'est voulu (le test `test_memoire_rappelee_dans_le_systeme` lit `agent.memoire` après coup), et c'est la raison pour laquelle `memoire_client()` fabriquera des souvenirs neufs à chaque appel.

**L'horloge** : celle de l'appelant, ou une horloge neuve au jour 90, `Horloge(JOUR_COURANT * 86_400)`, soit 7 776 000 s. On teste `is not None` pour la même raison que la session.

**Le journal et l'approbateur.** `JournalAudit(self.horloge)` partage l'horloge de l'agent : chaque entrée porte l'instant simulé, et après le refus par délai du scénario (c), les entrées suivantes sont datées 120 s plus tard. `Approbateur(self.horloge, self.journal)` reçoit la même horloge (qu'il avance quand l'humain ne répond pas) et le même journal (où il note « refus par délai »). Son délai par défaut est de 120 s, et sa liste de réponses humaines est vide : sans réponse prévue, toute demande d'approbation est refusée.

**Les virements** : une liste vide, le « cœur bancaire » simulé. C'est la seule chose au monde que l'agent peut modifier de façon irréversible, et la seule ligne qui y écrit est la dernière de l'outil de virement (palier 09).

**Le registre, dans l'ordre de 77.** `enregistrer_recherche(Registre())` crée un registre neuf, y enregistre l'outil de recherche et rend le registre, ce qui permet d'écrire les deux en une ligne. `enregistrer_outils_metier` ajoute les cinq outils de calcul. `enregistrer_virement` ajoute l'outil irréversible, en lui passant l'approbateur, le journal et la liste des virements de **cet** agent. Chaque fonction d'enregistrement modifie le registre qu'elle reçoit : c'est pour cela que les deux dernières lignes n'ont pas besoin d'affectation.

**Les outils protégés.** `proteger(self.registre, self.session, self.journal)` rend le dictionnaire nom → appelable que la boucle utilisera. Chaque appelable vérifie la politique (et journalise la décision), lève `RefusPolitique` si le rôle n'a pas le droit, puis passe par la porte du registre, qui valide le schéma, et seulement ensuite exécute l'outil. C'est l'équivalent d'un aspect `@PreAuthorize` suivi d'un `@Valid` autour de chaque méthode métier. `proteger` reçoit la session de l'agent et la relit à chaque appel.

**Les définitions pour le modèle.** `definitions_api()` rend les sept définitions au format de l'API, avec `"strict": True` et les bornes déplacées dans les descriptions (palier 04). Elles sont calculées une fois : la liste envoyée au modèle reste identique d'une requête à l'autre.

**Pourquoi ne rien appeler ici ?** Un constructeur qui câble ne fait aucun travail métier : pas d'appel au modèle, pas de recherche, pas d'écriture au journal. On peut donc créer un agent dans un test sans effet de bord, exactement comme on démarre un contexte Spring sans déclencher de traitement.

```text
# [extrait] console
>>> from agent.assemblage import Agent
>>> from agent.modele import FakeLLM
>>> agent = Agent(FakeLLM([]))
>>> list(agent.outils)
['rechercher_reglementation', 'mensualite', 'ratio_endettement', 'convertir_aed_usd', 'gratuite_fin_de_service', 'tva', 'initier_virement']
>>> agent.horloge.jour(), agent.session, agent.virements
(90.0, {'role': 'client_banque', 'portees': {'lecture', 'virement:initier'}}, [])
>>> agent.schemas[1]["input_schema"]["properties"]["n_mois"]
{'type': 'integer', 'description': 'Contraintes : minimum=1, maximum=300.'}
```

L'ordre d'affichage des portées peut varier d'une exécution à l'autre, puisqu'un `set` n'a pas d'ordre ; le reste est fixe.

## Ce qui passe maintenant

Aucun test du palier ne passe encore : ils appellent tous `repondre` ou un scénario. Le constructeur sera vérifié à l'étape suivante, par `test_agent_accepte_n_importe_quel_port`.
