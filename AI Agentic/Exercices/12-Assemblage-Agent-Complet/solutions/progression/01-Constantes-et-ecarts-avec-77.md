# Étape 1 — Les constantes et ce qui change depuis 77

> Palier 12 · Étape 1 sur 8 · Suivant : [Étape 2 — Le constructeur de l'Agent, ou le câblage](<02-Agent-le-cablage.md>) · Énoncé : [README du palier 12](<../../README.md>)

## Comment raisonner depuis la feuille blanche

Un fichier d'assemblage s'écrit dans l'ordre inverse d'un module de calcul. Dans un module de calcul, on part d'une formule et l'on écrit la fonction qui la calcule. Ici, il n'y a presque rien à calculer : tout existe déjà dans les onze modules. La première question est donc **de quoi l'agent a-t-il besoin, et où cela se trouve-t-il ?** On répond en écrivant les imports, palier par palier, en suivant le trajet d'une question : la mémoire la complète, le prompt la met en forme, la boucle interroge le modèle, les outils protégés agissent, le journal garde la trace, l'évaluation juge le tout.

La deuxième question est : **qu'est-ce qui vient de l'extérieur de l'agent ?** Le jour courant, la session authentifiée, l'IBAN du promoteur dans le scénario du virement. Ce sont des données d'entrée, pas de la logique : on les écrit en constantes en tête de fichier, et l'agent les recevra en paramètre.

Avant de coder, relis la section « Ce qui change par rapport à l'étape 77 » de l'énoncé : c'est elle qui explique la forme de ce fichier.

## Pourquoi pas les variables globales de 77

Dans l'étape 77, l'état de l'agent est global :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`lancer(script, question)`** — Cette fonction de l'étape 77, vue ici seulement par sa signature et sa docstring, ressemble à un employé qui travaille sur un bureau commun où chacun laisse traîner ses dossiers. Elle reçoit le script du faux modèle et la question du client, et fait tourner l'agent en lisant et en modifiant au passage quatre objets globaux qu'elle ne reçoit pas : l'horloge réglée au jour 90, le journal, la session `client_banque` et la liste des virements. Le résultat qu'elle rend est un dictionnaire, mais l'état qu'elle laisse derrière elle reste dans ces globales, si bien qu'un test qui change la session ou approuve un virement contamine tous ceux qui le suivent.

```python
# [extrait] brouillon
from agent.modele import Horloge

HORLOGE = Horloge(90 * 86_400.0)
JOURNAL: list[str] = []
SESSION = {"role": "client_banque", "portees": {"lecture", "virement:initier"}}
VIREMENTS: list[dict] = []


def lancer(script: list, question: str) -> dict:
    """Utilise HORLOGE, JOURNAL, SESSION et VIREMENTS sans les recevoir."""
    ...
```

Dans un seul programme qui s'exécute une fois de haut en bas, cela marche. Dans une suite de tests, c'est une source d'erreurs. Le test de la session publique doit changer `SESSION`, puis la remettre à l'identique, sinon tous les tests suivants tournent sous le rôle `assistant_public` ; 77 l'écrit à la main avec `SESSION.update(...)` avant et après. Un virement approuvé dans un test reste dans `VIREMENTS` pour le suivant ; 77 appelle `VIREMENTS.clear()`. Et le journal mélange les entrées de tous les scénarios : pour isoler celles du scénario (c), 77 retient l'indice `debut = len(JOURNAL)`. L'ordre des tests devient significatif, et un test qui échoue au milieu laisse l'état sale pour les autres.

En Java, tu reconnais le problème des champs `static` mutables dans un service Spring : on les remplace par des beans injectés, un par contexte. Ici, chaque `Agent` aura sa propre horloge, son journal, sa session et sa liste de virements, et chaque test fabriquera le sien.

## Les imports et les constantes

```python
# [extrait] agent/assemblage.py
import json

from agent.boucle import executer_agent
from agent.evaluation import SEUILS, barriere_ci, noter, rapport
from agent.garde_fous import Approbateur, JournalAudit, enregistrer_virement, proteger
from agent.memoire import Souvenir, rappeler
from agent.metier import fr, mensualite, ratio_endettement
from agent.modele import FakeLLM, Horloge, Reponse, appel_outil, construire_prompt, texte
from agent.outils import Registre, enregistrer_outils_metier
from agent.recherche import citations, enregistrer_recherche, plonger_texte

JOUR_COURANT = 90.0                            # jour 90 de la relation avec le client
SESSION_CLIENT = {"role": "client_banque", "portees": {"lecture", "virement:initier"}}   # vient de l'authentification
IBAN_PROMOTEUR = "AE07 0331 2345 6789 0123 456"
```

**`import json`** sert à écrire les arguments des outils dans le journal et à transformer les sorties d'outils en textes, les sources de la fidélité approchée.

**Les imports du paquet**, dans l'ordre alphabétique des modules, chacun venant d'un palier :

- `executer_agent` (palier 05) : la boucle ReAct, avec ses cinq statuts d'arrêt.
- `SEUILS`, `barriere_ci`, `noter`, `rapport` (palier 10) : la mesure d'un cas, l'agrégation avec Wilson, et la décision de déploiement.
- `Approbateur`, `JournalAudit`, `enregistrer_virement`, `proteger` (palier 09) : l'humain dans la boucle, le journal masqué et chaîné, l'outil irréversible et l'enveloppe de politique.
- `Souvenir`, `rappeler` (palier 06) : la mémoire et son score de pertinence.
- `fr`, `mensualite`, `ratio_endettement` (palier 03) : l'affichage français des montants et les deux calculs dont `demande_credit` a besoin pour fabriquer ses variantes.
- `FakeLLM`, `Horloge`, `Reponse`, `appel_outil`, `construire_prompt`, `texte` (palier 01) : le port de test, le temps simulé, les blocs d'une réponse scriptée et le prompt qui encadre les documents.
- `Registre`, `enregistrer_outils_metier` (palier 04) : le registre et les cinq outils de calcul.
- `citations`, `enregistrer_recherche`, `plonger_texte` (palier 07) : la lecture des `[REG-n]` d'une réponse, l'outil de recherche hybride, et la fonction texte → vecteur que la mémoire attend.

Remarque ce qui **manque** : ni `planification` (palier 08) ni `production` (palier 11). La boucle ReAct choisit ses étapes une à une, elle n'exécute pas un plan fixé d'avance ; et la production se branche autour du port du modèle, pas dans l'agent. Les deux branchements sont des défis bonus, traités à l'étape 8.

**`JOUR_COURANT = 90.0`** : le jour 90 de la relation avec le client, le repère de la mémoire. L'horloge par défaut de l'agent démarrera à 90 × 86 400 = 7 776 000 secondes.

**`SESSION_CLIENT`** : le rôle et les portées du client authentifié. Le commentaire est la règle de sécurité la plus importante du fichier : la session **vient de l'authentification**, jamais du modèle. Le modèle ne peut pas s'accorder la portée `virement:initier` en l'écrivant dans un message. C'est l'équivalent du `SecurityContext` de Spring Security, rempli par le filtre d'authentification et lu par `@PreAuthorize`. Les portées sont un `set`, ce qui rend le test « toutes les portées requises sont-elles présentes ? » trivial (palier 09).

**`IBAN_PROMOTEUR`** : l'IBAN du courriel piégé, valide au sens du contrôle mod 97 (palier 03). Il est valide exprès : le garde-fou ne doit pas compter sur un IBAN mal formé pour refuser le virement, il doit le refuser parce qu'aucun humain ne l'a approuvé.

**Le piège classique** est de modifier `SESSION_CLIENT` dans un test, par exemple `SESSION_CLIENT["portees"].add("admin")`. Comme c'est un dictionnaire partagé par tout le module, tous les agents créés ensuite hériteraient de la portée. L'étape 2 empêche cela : l'agent garde une **copie** de la session.

## Ce qui passe maintenant

Rien encore : les constantes étaient déjà dans le squelette. Vérifie seulement que le module s'importe, depuis `projet/` :

```text
python -c "import agent.assemblage"
```

La commande ne doit rien afficher. Les 15 tests du palier échouent toujours par `NotImplementedError`, et les 150 tests des paliers précédents passent.
