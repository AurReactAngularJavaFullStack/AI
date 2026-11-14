# Palier 04 — Registre d'outils

> Palier 04 sur 12 · Précédent : [Palier 03 — Outils métier EAU](<../03-Outils-Metier-EAU/README.md>) · Suivant : [Palier 05 — Boucle d'agent](<../05-Boucle-d-Agent/README.md>) · Leçons à relire : [Étape 12 — Outils](<../../03-Schemas-Outils-et-Premiere-Evaluation/12-Outils-Definitions-Fondamentaux.md>) · [Étape 13 — Six agents EAU](<../../03-Schemas-Outils-et-Premiere-Evaluation/13-Agent-Exemples-Cas-Usage.md>) · [Étape 46 — MCP](<../../09-MCP/46-MCP-Definitions-Fondamentaux.md>) · [Étape 47 — MCP, exemples](<../../09-MCP/47-MCP-Exemples-Cas-Usage.md>) · [Étape 48 — MCP par domaine](<../../09-MCP/48-MCP-Applications-Domaines.md>) · [Étape 49 — Disponibilité MCP](<../../09-MCP/49-MCP-Formule-Score-de-Disponibilite.md>) · [Étape 77 — Projet final](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Mode d'emploi : [les douze paliers](<../README.md>)

Un outil est la seule façon dont un agent agit sur le monde. Le modèle ne fait que **demander** un appel, sous la forme d'un bloc `tool_use` qui porte un nom et des arguments ; c'est ton code qui décide d'exécuter, et qui exécute. Ce palier construit la pièce qui se place entre les deux : un registre où chaque outil a un nom public, une description pour le modèle et un schéma ; une porte qui refuse des arguments mal formés **avant** d'appeler la fonction ; et une enveloppe qui renvoie toute erreur au modèle au lieu de faire tomber l'agent.

## Où en est l'agent

Trois paliers sont faits. Le palier 01 (`agent/modele.py`) a posé le port du modèle, `FakeLLM`, et la fonction `appel_outil`, qui fabrique un bloc `tool_use`. Le palier 02 (`agent/schemas.py`) a écrit `validate`, `objet` et `schema_pour_api_strict`. Le palier 03 (`agent/metier.py`) a écrit les calculs exacts : mensualité, ratio d'endettement, fin de service, TVA, change. Ces calculs ne sont pas encore appelables par le modèle : il ne les connaît pas, et rien ne vérifie ce qu'il leur enverrait.

```text
                ┌───────────────────────────────────── agent ──────────────────────────────────────┐
  question ───► │ construire_prompt (01) ──► boucle (05) ── tool_use ──► ╔═══════════════════════╗ │
                │                              ▲   ▲                     ║ outils.py (04)  ◄ ICI ║ │
                │    definitions_api ──────────┘   │                     ║ Registre, porte,      ║ │
                │    (ce que le modèle voit)       └── tool_result ◄──── ║ executer_appel        ║ │
                │                                  (succès ou is_error)  ╚════════╤══════════════╝ │
                │                                                                 │                │
                │                                   validate (02)  ◄──────────────┤                │
                │                                   metier.py (03) ◄──────────────┘                │
                └──────────────────────────────────────────────────────────────────────────────────┘
```

Dans la boucle percevoir → décider → agir → observer, ce module intervient deux fois. Pour **décider**, le modèle reçoit `Registre.definitions_api()`, la liste des outils au format de l'API : c'est ce qui définit ce que l'agent **peut** faire. Pour **agir** et **observer**, la boucle du palier 05 passera chaque bloc `tool_use` à `executer_appel`, qui appelle la porte de l'outil et rend un `tool_result` : la sortie en JSON, ou l'erreur marquée `is_error`, que le modèle lira à l'étape suivante pour se corriger.

Pour un développeur Spring, le registre joue le rôle du conteneur de beans : `@registre.outil(...)` ressemble à une annotation `@Component` qui inscrit la méthode sous un nom ; `porte(nom)` est l'aspect qui applique `@Valid` avant d'entrer dans la méthode ; `executer_appel` est le `@ControllerAdvice` qui transforme toute exception en une réponse d'erreur lisible. La différence : un décorateur Python n'est pas une métadonnée lue plus tard par un framework, c'est une fonction exécutée tout de suite, à la définition.

### Ce qui change par rapport à l'étape 77

- **Plus de variable globale.** Dans 77, `REGISTRE` est un dictionnaire global et le décorateur `outil` y écrit. Ici, `Registre` est un objet, passé en paramètre : chaque agent, et chaque test, a le sien, et deux tests ne se marchent pas dessus.
- **Des méthodes au lieu de fonctions globales.** Le décorateur devient `Registre.outil`, et `porte`, `definitions_api` deviennent des méthodes ; `appelables` remplace `OUTILS_AGENT = {nom: porte(nom) for nom in REGISTRE}`.
- **La porte ne vérifie que le schéma.** Dans 77, `porte` vérifie d'abord la politique (rôle, portées), puis le schéma. La politique arrive au palier 09, avec `proteger(registre, session, journal)`, qui enveloppe `registre.porte(nom)` sans modifier ce module : on compose, on ne réécrit pas.
- **Une fonction pour l'enveloppe d'erreur.** Dans 77, le `try`/`except` qui transforme une exception en `tool_result` marqué `is_error` est écrit au milieu de la boucle. Ici, il devient `executer_appel`, testable seule : elle rend toujours une enveloppe et ne laisse jamais sortir d'exception.
- **Deux contrôles plus tôt.** Un nom vide ou déjà pris est refusé dès l'appel `registre.outil(...)`, avant même de décorer ; un nom inconnu est refusé dès la fabrication de la porte.

## Ce que tu vas coder

- `Outil` et les trois exceptions `RefusPolitique`, `ArgumentsInvalides`, `ErreurOutil` sont fournis dans le squelette : relis-les, tout le reste s'appuie dessus.
- `Registre.__len__` et `Registre.__contains__` : `len(registre)` et `"tva" in registre`.
- `Registre.outil(nom, description, schema)` : le décorateur qui enregistre une fonction avec son contrat.
- `Registre.porte(nom)` : l'appelable qui valide les arguments, puis seulement appelle la fonction.
- `Registre.appelables()` : le dictionnaire nom → porte que l'on passera à la boucle.
- `Registre.definitions_api()` : la liste des outils au format de l'API, en mode strict.
- `executer_appel(outils, bloc)` : un bloc `tool_use` en entrée, un `tool_result` et une ligne de trace en sortie, sans jamais lever.
- `enregistrer_outils_metier(registre)` : les cinq outils de calcul du palier 03, avec leurs schémas.

## Rappel de cours

### La porte : le schéma avant la fonction

Pour un outil o, de fonction fₒ et de schéma Sₒ, la porte reçoit des arguments x et ne laisse passer que des arguments conformes. Avec V(x, S) la liste des écarts que rend `validate` :

$$
\text{porte}_o(x) = \begin{cases} f_o(x) & \text{si } V(x, S_o) = \varnothing \\ \text{lever ArgumentsInvalides} & \text{sinon} \end{cases}
$$

La conséquence qui compte : fₒ n'est **jamais** appelée sur des arguments non conformes. Les fonctions du palier 03 supposent des nombres ; sur `n_mois = "300"`, la comparaison `"300" <= 0` lèverait `TypeError` au milieu du calcul. La porte fait du schéma une précondition : les fonctions métier ne voient que des entrées bien formées (étape 9, point 5).

### L'enveloppe d'erreur : pourquoi renvoyer plutôt que lever

Une erreur renvoyée au modèle dans un `tool_result` marqué `is_error` lui donne une chance de se corriger à l'étape suivante. Si le modèle produit un appel correct avec une probabilité p à chaque essai, et qu'on lui laisse R relances après une erreur, la probabilité qu'au moins un essai réussisse vaut (palier 02, `p_succes`) :

$$
P_{succes} = 1 - (1 - p)^{R + 1}
$$

Avec p = 0,9 (illustratif) et R = 2, P = 1 − 0,1³ = 0,999. Si l'exception sortait de la boucle, l'agent s'arrêterait au premier échec : R = 0 et P = 0,9. L'enveloppe transforme une panne en information.

### Le registre, source unique du contrat

Le schéma d'un outil sert au moins deux fois : à la porte, pour valider, et à `definitions_api`, pour dire au modèle ce qu'il peut envoyer ; un serveur MCP en ferait un troisième usage (`tools/list`, étape 46). Sans registre, chacun des N consommateurs garde sa copie du contrat de chacun des M outils ; avec le registre, on écrit M contrats et N lecteurs :

$$
I_{sans} = N \times M
$$

$$
I_{avec} = N + M
$$

L'écart se factorise, ce qui montre qu'il est positif ou nul dès que N ≥ 2 et M ≥ 2 :

$$
N M - (N + M) = (N - 1)(M - 1) - 1
$$

Avec N = 2 consommateurs (la porte et l'API) et M = 5 outils : 10 copies à tenir synchrones contre 7 pièces. Avec un serveur MCP en plus (N = 3) : 15 contre 8. Surtout, une seule copie ne peut pas diverger d'elle-même.

### Le mode strict : des bornes qui ne partent pas à l'API

En mode strict, l'API contraint le décodage du modèle au schéma fourni, mais refuse les bornes (`minimum`, `maximum`, `exclusiveMinimum`, `minLength`, `maxLength`). `schema_pour_api_strict` (palier 02) les retire et les recopie dans la description. Le modèle est donc garanti d'envoyer un entier pour `n_mois`, mais pas un entier entre 1 et 300 : **seule la porte locale vérifie les bornes**. C'est pourquoi `definitions_api` envoie le schéma allégé, alors que la porte garde le schéma complet.

### Les symboles, un par un

$$
o
$$

Un outil enregistré, de type `Outil` : nom, description, schéma, fonction.

$$
x
$$

Les arguments que le modèle envoie, un dictionnaire JSON ; le champ `input` du bloc `tool_use`, passé à la porte par `**arguments`.

$$
f_o
$$

La fonction métier de l'outil, par exemple `outil_mensualite` ; le champ `fonction` de `Outil`.

$$
S_o
$$

Le schéma complet de l'outil, bornes comprises ; le champ `schema` de `Outil`.

$$
V(x, S)
$$

La liste des écarts entre x et S, chacun avec son chemin JSON ; ce que rend `validate(x, S)`. Vide si x est conforme.

$$
p
$$

La probabilité qu'un appel du modèle soit correct à un essai donné, entre 0 et 1 ; une valeur mesurée, illustrative ici.

$$
R
$$

Le nombre de relances qu'on laisse au modèle après une erreur, un entier positif ou nul.

$$
P_{succes}
$$

La probabilité qu'au moins un des R + 1 essais réussisse.

$$
N
$$

Le nombre de consommateurs du contrat des outils (validation, API, serveur MCP…).

$$
M
$$

Le nombre d'outils ; 5 dans ce palier.

$$
I
$$

Le nombre de pièces à écrire et à tenir synchrones, sans registre ou avec.

## Spécification

Le registre garde ses outils dans `self.outils`, un `dict[str, Outil]` : un dictionnaire Python conserve l'ordre d'insertion, et cet ordre est celui de `definitions_api` et des tests. Les exemples ci-dessous utilisent `registre_metier()`, c'est-à-dire `enregistrer_outils_metier(Registre())`.

### Outil et les trois exceptions (fournis)

```python
# [extrait] spécification
@dataclass
class Outil:
    nom: str
    description: str
    schema: dict
    fonction: Callable


class RefusPolitique(PermissionError): ...
class ArgumentsInvalides(ValueError): ...
class ErreurOutil(Exception): ...
```

`Outil` est un simple porteur de données, l'équivalent d'un `record` Java. Les trois exceptions distinguent **qui** a dit non : la politique (`RefusPolitique`, levée au palier 09, sous-classe de `PermissionError`), le schéma (`ArgumentsInvalides`, sous-classe de `ValueError`, parce que ce sont des arguments de valeur interdite), l'outil lui-même (`ErreurOutil` : outil inconnu, garde-fou interne, refus humain). Le nom de la classe partira tel quel au modèle, en tête du message d'erreur. Test : `TestRegistre.test_hierarchie_des_exceptions`.

### Registre, `__len__` et `__contains__`

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.__init__()`** — Le constructeur, fourni dans le squelette, ouvre le grand livre vide d'un archiviste qui s'apprête à inscrire chaque outil de l'agent sous son nom : il ne reçoit rien et crée l'attribut `self.outils`, un dictionnaire vide qui associera chaque nom à un objet `Outil` et gardera l'ordre d'inscription. Chaque agent, et chaque test, crée ainsi son propre registre, au lieu de partager la variable globale `REGISTRE` de l'étape 77, si bien que deux tests ne peuvent pas se marcher sur les pieds.

**`Registre.__len__()`** — Cette méthode spéciale doit répondre à la question que pose l'archiviste en refermant son livre, combien d'outils sont inscrits : elle ne reçoit rien, et c'est elle que Python appelle quand on écrit `len(registre)`, pour renvoyer le nombre d'entrées de `self.outils`, sous forme d'entier. Après l'inscription des outils métier par `enregistrer_outils_metier`, elle doit renvoyer 5, ce que vérifie le test `TestRegistre.test_cinq_outils_metier`.

**`Registre.__contains__(nom)`** — Celle-ci doit permettre de demander à l'archiviste, d'un seul mot, si un outil figure dans son livre : elle reçoit un nom et renvoie un booléen qui dit si un outil porte ce nom, et c'est elle que Python appelle derrière l'opérateur `in`. Sur le registre métier, `"tva" in registre` doit donc être vrai, tandis qu'un nom comme « virement », jamais inscrit, doit donner faux.

```python
# [extrait] spécification
class Registre:
    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    def __contains__(self, nom: str) -> bool: ...
```

`__init__` est fourni : il crée la table vide `self.outils`. `len(registre)` rend le nombre d'outils et `nom in registre` dit si un outil porte ce nom. **Exemple.** Après `enregistrer_outils_metier(Registre())`, `len(registre)` vaut 5, `list(registre.outils)` vaut `["mensualite", "ratio_endettement", "convertir_aed_usd", "gratuite_fin_de_service", "tva"]`, et `"tva" in registre` est vrai. Test : `TestRegistre.test_cinq_outils_metier`.

### Registre.outil

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.outil(nom, description, schema)`** — Ce décorateur à paramètres doit jouer le rôle du greffier qui, avant même de lire le dossier, vérifie que le nom proposé est libre : il reçoit le nom public de l'outil, sa description pour le modèle et son schéma, et lève aussitôt `ValueError` si le nom est vide ou déjà inscrit dans le registre. Sinon, il renvoie une fonction `enregistrer(fonction)` que Python applique à la fonction décorée ; elle range un `Outil` qui réunit les quatre informations dans `self.outils` et rend la fonction inchangée, toujours appelable directement. Ainsi, une fonction « double » décorée par ce greffier donne toujours 8 pour 4, et une seconde inscription sous le nom « tva » est refusée avant toute décoration.

```python
# [extrait] spécification
class Registre:
    def outil(self, nom: str, description: str, schema: dict): ...
```

Décorateur à paramètres. L'appel `registre.outil(nom, description, schema)` vérifie le nom **tout de suite** : un nom vide lève `ValueError`, un nom déjà enregistré aussi. Il rend une fonction `enregistrer(fonction)`, que Python applique à la fonction décorée : elle range `Outil(nom, description, schema, fonction)` dans la table et rend la fonction **inchangée**, qui reste appelable directement.

**Exemple.** Avec `r = Registre()`, on décore `def double(x): return 2 * x` par `@r.outil("double", "Double un nombre.", objet({"x": {"type": "number"}}))`. Ensuite, `double(4)` vaut 8 et `r.outils["double"].fonction` est `double`. Sur un registre qui contient déjà « tva », l'appel `r.outil("tva", "doublon", objet({}))` lève `ValueError` avant toute décoration, et `r.outil("", "sans nom", objet({}))` aussi. Tests : `TestRegistre.test_le_decorateur_rend_la_fonction`, `TestRegistre.test_nom_deja_pris_ou_vide`.

### Registre.porte

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.porte(nom)`** — Cette méthode doit fabriquer le portier qui se tient devant la salle de chaque outil et ne laisse entrer que des arguments en règle : elle reçoit un nom, lève `ValueError` dès la fabrication si aucun outil ne le porte, et renvoie sinon une fonction `appeler(**arguments)`. Celle-ci valide les arguments contre le schéma complet de l'outil, bornes comprises, lève `ArgumentsInvalides` avec les écarts joints par « ; » s'il y en a, et seulement sinon appelle la fonction de l'outil avec les mêmes arguments et renvoie sa sortie. La porte de « mensualite » doit ainsi rendre une mensualité de 5558,32 AED pour 1 000 000 AED à 4,5 % sur 300 mois, tandis qu'une chaîne « 3 » à la place d'un entier est arrêtée avant que la fonction ne soit jamais appelée.

```python
# [extrait] spécification
class Registre:
    def porte(self, nom: str) -> Callable: ...
```

Un nom inconnu lève `ValueError` dès la fabrication de la porte. Sinon, rend une fonction `appeler(**arguments)` qui valide `arguments` contre le schéma complet de l'outil ; s'il y a des écarts, elle lève `ArgumentsInvalides` avec les écarts joints par « ; » ; sinon, elle appelle la fonction de l'outil avec les mêmes arguments et rend sa sortie.

**Exemple.** `registre_metier().porte("mensualite")(principal=1_000_000, taux_annuel=0.045, n_mois=300)` rend `{"mensualite_aed": 5558.32}`. Pour un outil « compter » de schéma `objet({"n": {"type": "integer", "minimum": 1}})` dont la fonction note chaque appel dans une liste `appels` : `porte("compter")(n="3")` lève `ArgumentsInvalides` de message `$.n : type attendu integer, reçu string` ; `porte("compter")(n=1, bonus=True)` lève `ArgumentsInvalides` (`$ : champ non prévu « bonus »`) ; et `appels` reste vide, preuve que la fonction n'a jamais été appelée. `registre_metier().porte("virement")` lève `ValueError`. Tests : `TestPorte.test_appel_valide`, `test_le_schema_arrete_avant_la_fonction`, `test_outil_inconnu`.

### Registre.appelables

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.appelables()`** — Cette méthode doit remettre à la boucle d'agent le trousseau complet des portes, une clé par outil, comme un concierge qui confie au gardien de nuit toutes les clés de l'immeuble rangées dans l'ordre des étages : elle ne reçoit rien et renvoie un dictionnaire qui associe chaque nom d'outil à sa porte, dans l'ordre du registre. C'est l'argument `outils` que recevra la boucle du palier 05 ; la porte de « tva », appelée avec un montant hors taxe de 12 000, doit renvoyer 600 AED de TVA et 12 600 AED TTC.

```python
# [extrait] spécification
class Registre:
    def appelables(self) -> dict[str, Callable]: ...
```

Rend un dictionnaire nom → porte, une entrée par outil, dans l'ordre du registre. C'est l'argument `outils` de la boucle du palier 05. **Exemple.** `registre_metier().appelables()["tva"](montant_ht=12_000)` rend `{"tva_aed": 600.0, "ttc_aed": 12600.0}`. Test : `TestOutilsMetier.test_sorties_arrondies_comme_dans_77`.

### Registre.definitions_api

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Registre.definitions_api()`** — Cette méthode doit rédiger le catalogue que l'on tend au modèle pour lui dire ce que l'agent sait faire, comme un maître d'hôtel qui présente la carte sans montrer la cuisine : elle ne reçoit rien et renvoie une liste de dictionnaires, un par outil dans l'ordre du registre, avec les quatre clés `name`, `description`, `input_schema` et `strict`. Le schéma envoyé est celui que produit `schema_pour_api_strict`, sans bornes, celles-ci étant recopiées dans les descriptions, et `strict` vaut toujours `True`. Pour « mensualite », la durée devient ainsi un entier décrit par « Contraintes : minimum=1, maximum=300. », et aucun des cinq mots-clés de bornes ne doit subsister dans les cinq définitions.

```python
# [extrait] spécification
class Registre:
    def definitions_api(self) -> list[dict]: ...
```

Rend une définition par outil, dans l'ordre du registre, avec quatre clés : `name` (le nom), `description`, `input_schema` (le schéma passé par `schema_pour_api_strict`) et `strict` (toujours `True`).

**Exemple à la main**, pour `n_mois`, dont le schéma complet est `{"type": "integer", "minimum": 1, "maximum": 300}`. `schema_pour_api_strict` garde `type`, retire `minimum` et `maximum`, fabrique la liste des contraintes retirées, `minimum=1` puis `maximum=300`, et l'écrit dans la description, qui était vide : « Contraintes : minimum=1, maximum=300. ». Le résultat vaut `{"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}`. La définition complète de « mensualite » est :

```json
{
  "name": "mensualite",
  "description": "Mensualité d'un prêt amortissable, en AED.",
  "input_schema": {
    "type": "object",
    "required": ["principal", "taux_annuel", "n_mois"],
    "additionalProperties": false,
    "properties": {
      "principal": {"type": "number", "description": "Contraintes : exclusiveMinimum=0."},
      "taux_annuel": {"type": "number", "description": "Contraintes : minimum=0, maximum=0.3."},
      "n_mois": {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}
    }
  },
  "strict": true
}
```

Les cinq définitions ont `strict` à vrai, et aucun des cinq mots-clés de bornes n'apparaît dans leur sérialisation JSON. Test : `TestDefinitionsApi.test_mode_strict_sans_bornes`.

### executer_appel

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`executer_appel(outils, bloc)`** — Cette fonction doit être l'agent de liaison qui porte chaque demande du modèle jusqu'au bon outil et revient toujours avec un compte rendu, même quand tout a mal tourné : elle reçoit le dictionnaire nom → appelable et un bloc `tool_use`, et renvoie un couple (résultat, ligne de trace) sans jamais lever. En cas de succès, le résultat est un `tool_result` qui porte l'identifiant du bloc et la sortie sérialisée en JSON, et la trace reprend le nom, les arguments et la sortie ; en cas d'échec, quelle que soit l'exception, le contenu devient « NomDeLaClasse: message » avec `is_error` à vrai et la trace se termine par « ERREUR ». Un outil absent du dictionnaire compte comme une `ErreurOutil` « outil inconnu » ; ainsi un appel « tva » sur 100 AED doit rendre 5 AED de TVA et 105 AED TTC, et un appel « pirater » une erreur que le modèle pourra lire.

```python
# [extrait] spécification
def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]: ...
```

`outils` est un dictionnaire nom → appelable (en pratique `appelables()`), `bloc` un bloc `tool_use` (attributs `id`, `name`, `input`). La fonction rend un couple (résultat, ligne de trace) et **ne lève jamais**.

- Succès : le résultat vaut `{"type": "tool_result", "tool_use_id": bloc.id, "content": json.dumps(sortie, ensure_ascii=False)}` et la trace `(bloc.name, bloc.input, sortie)`.
- Échec, quelle que soit l'exception `e` : le résultat a pour `content` le texte « NomDeLaClasse: message » (`f"{type(e).__name__}: {e}"`) et la clé `is_error` à `True` ; la trace vaut `(bloc.name, bloc.input, f"ERREUR {e}")`.
- Un nom absent du dictionnaire est traité comme un échec, par une `ErreurOutil` de message « outil inconnu : nom ».

**Exemple.** Le bloc `appel_outil("tva", {"montant_ht": 100}, "t1")` donne 100 × 0,05 = 5 AED de TVA et 105 AED TTC : le résultat vaut `{"type": "tool_result", "tool_use_id": "t1", "content": '{"tva_aed": 5.0, "ttc_aed": 105.0}'}`, sans clé `is_error`, et la trace `("tva", {"montant_ht": 100}, {"tva_aed": 5.0, "ttc_aed": 105.0})`. Le bloc « mensualite » avec `n_mois` égal à la chaîne « 300 » donne `is_error` vrai et le contenu `ArgumentsInvalides: $.n_mois : type attendu integer, reçu string` ; la trace se termine par `ERREUR $.n_mois : type attendu integer, reçu string`. Avec un dictionnaire vide, le bloc `appel_outil("pirater", {}, "x")` donne le contenu `ErreurOutil: outil inconnu : pirater` et la trace `("pirater", {}, "ERREUR outil inconnu : pirater")`. Tests : `TestExecuterAppel.test_succes`, `test_erreur_renvoyee_avec_is_error`, `test_outil_inconnu`.

### enregistrer_outils_metier

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`enregistrer_outils_metier(registre)`** — Cette fonction doit être la cérémonie d'embauche des cinq calculateurs du palier 03, chacun présenté au registre avec son badge, sa fiche de poste et son contrat : elle reçoit un registre, y inscrit dans l'ordre les outils « mensualite », « ratio_endettement », « convertir_aed_usd », « gratuite_fin_de_service » et « tva », avec les descriptions du tableau et des schémas construits par `objet`, puis renvoie ce même registre. Chaque outil enveloppe la fonction métier correspondante et arrondit sa sortie, au centime ou à quatre décimales pour le ratio ; le ratio de C-1 doit ainsi valoir 0,289 et être recevable, la conversion de 5 558,32 AED donner 1 513,5 USD, et le plafond des retraités rester hors de portée du modèle.

```python
# [extrait] spécification
def enregistrer_outils_metier(registre: Registre) -> Registre: ...
```

Enregistre, dans cet ordre, les cinq outils du tableau, avec des schémas construits par `objet` (tous les champs obligatoires, aucun champ non prévu), et rend le registre. Chaque fonction enveloppe la fonction du palier 03 et arrondit sa sortie.

#### Les cinq outils métier

| Nom | Description | Arguments et bornes du schéma | Sortie |
| --- | --- | --- | --- |
| `mensualite` | Mensualité d'un prêt amortissable, en AED. | `principal` nombre > 0 ; `taux_annuel` nombre dans [0 ; 0,3] ; `n_mois` entier dans [1 ; 300] | `{"mensualite_aed": …}`, au centime |
| `ratio_endettement` | Endettement total CBUAE : (mensualités existantes + nouvelle) / revenu, plafond 50 %. | `existantes` nombre ≥ 0 ; `nouvelle` nombre > 0 ; `revenu` nombre > 0 | `{"ratio": …, "recevable": …}`, ratio à 4 décimales |
| `convertir_aed_usd` | Convertit un montant en AED vers l'USD, à la parité fixe de 3,6725 AED pour 1 USD. | `montant_aed` nombre ≥ 0 | `{"montant_usd": …}`, au centime |
| `gratuite_fin_de_service` | Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé), en AED. | `salaire_base_mensuel` nombre > 0 ; `annees` nombre dans [0 ; 60] | `{"indemnite_aed": …}`, au centime |
| `tva` | TVA de 5 % et montant TTC, en AED. | `montant_ht` nombre ≥ 0 | `{"tva_aed": …, "ttc_aed": …}`, au centime |

« > 0 » s'écrit `"exclusiveMinimum": 0`, « ≥ 0 » s'écrit `"minimum": 0`, et « dans [1 ; 300] » s'écrit `"minimum": 1, "maximum": 300`. L'outil de ratio garde le plafond par défaut de 50 % : le plafond des retraités n'est pas un argument que le modèle peut choisir.

**Exemples à la main.** `ratio_endettement` avec existantes = 6 000, nouvelle = 5 558,32 et revenu = 40 000 : le ratio vaut 11 558,32 / 40 000 = 0,288958, arrondi à 4 décimales 0,2890, d'où `{"ratio": 0.289, "recevable": True}`. `convertir_aed_usd` avec 5 558,32 : 5 558,32 / 3,6725 = 1 513,4976, arrondi au centime 1 513,50, d'où `{"montant_usd": 1513.5}`. `tva` avec 12 000 : `{"tva_aed": 600, "ttc_aed": 12600}` (600 et 12 000 + 600). `gratuite_fin_de_service` avec 10 000 et 7 : `{"indemnite_aed": 55000}`. Tests : `TestOutilsMetier.test_sorties_arrondies_comme_dans_77`, `TestRegistre.test_cinq_outils_metier`, `TestDefinitionsApi.test_mode_strict_sans_bornes`.

## Squelette algorithmique

```text
ALGORITHME Outil (décorateur du registre)
ENTRÉES : nom, description, schéma
SORTIE  : une fonction enregistrer
  SI nom est vide OU nom est déjà dans la table ALORS LEVER ErreurDeValeur
  RENDRE la fonction enregistrer(f) :
     table[nom] ← Outil(nom, description, schéma, f)
     RENDRE f                                    (la fonction décorée est inchangée)

ALGORITHME Porte
ENTRÉE  : nom
SORTIE  : une fonction appeler
  SI nom n'est pas dans la table ALORS LEVER ErreurDeValeur
  o ← table[nom]
  RENDRE la fonction appeler(arguments nommés x) :
     écarts ← validate(x, o.schéma)
     SI écarts n'est pas vide ALORS LEVER ArgumentsInvalides(écarts joints par « ; »)
     RENDRE o.fonction(x)

ALGORITHME Appelables
  RENDRE { nom : Porte(nom) POUR CHAQUE nom DE la table }

ALGORITHME DéfinitionsAPI
  RENDRE la liste, POUR CHAQUE outil o DE la table dans l'ordre, de
     { name : o.nom, description : o.description, input_schema : SchémaStrict(o.schéma), strict : vrai }

ALGORITHME ExécuterAppel
ENTRÉES : outils (nom → appelable), bloc (id, nom, arguments)
SORTIE  : (résultat, ligne de trace)
  ESSAYER
     SI bloc.nom n'est pas dans outils ALORS LEVER ErreurOutil(« outil inconnu : » bloc.nom)
     y ← outils[bloc.nom](bloc.arguments)
     RENDRE ({type : tool_result, tool_use_id : bloc.id, content : JSON(y)}, (bloc.nom, bloc.arguments, y))
  SAUF exception e
     RENDRE ({type : tool_result, tool_use_id : bloc.id, content : NomDeClasse(e) « : » message(e), is_error : vrai},
             (bloc.nom, bloc.arguments, « ERREUR » message(e)))
```

**Complexité.** Enregistrer un outil, tester un nom ou fabriquer une porte coûte O(1) en moyenne, grâce au dictionnaire. Un appel par la porte coûte la validation, linéaire dans la taille des arguments et du schéma (quelques champs ici), plus le coût de la fonction métier. `appelables` et `definitions_api` sont linéaires dans le nombre d'outils et la taille totale de leurs schémas ; on les appelle une fois, au démarrage de l'agent. `executer_appel` ajoute une sérialisation JSON, linéaire dans la taille de la sortie.

**Du squelette au code.** Les cinq algorithmes deviennent des méthodes de `Registre` ou des fonctions de `agent/outils.py`. Outil devient la méthode `outil`, dont la fonction interne s'appelle `enregistrer`. Porte devient `porte` et sa fonction interne `appeler`, qui reçoit ses arguments par `**arguments` et les repasse à la fonction métier de la même façon. Appelables devient `appelables`, une compréhension de dictionnaire qui appelle `porte`. DéfinitionsAPI devient `definitions_api`, qui délègue à `schema_pour_api_strict` du palier 02. ExécuterAppel devient `executer_appel`, avec un bloc `try` et un `except Exception` ; la sérialisation se fait par `json.dumps` avec `ensure_ascii=False`, pour garder les accents lisibles. Les cinq outils de `enregistrer_outils_metier` sont des fonctions internes décorées par `registre.outil`.

## Cas d'usage aux Émirats

Les montants et les taux d'erreur du modèle ci-dessous sont illustratifs ; les règles citées (plafond CBUAE, fin de service, TVA, frais DLD de 4 %) sont réelles, à confirmer avec le texte en vigueur.

### Banque — un taux écrit en pourcentage, arrêté avant le calcul

L'assistant de la banque B-1 reçoit : « hypothèque de 1 000 000 AED à 4,5 % sur 25 ans ». Le modèle appelle `mensualite` avec `taux_annuel` = 4.5 au lieu de 0.045. En mode strict, l'API garantit que c'est un nombre, mais elle ne porte pas la borne de 0,3 : seule la porte locale l'arrête. `executer_appel` rend un `tool_result` marqué `is_error`, de contenu `ArgumentsInvalides: $.taux_annuel : 4.5 > maximum 0.3`. Le modèle lit le chemin et la borne, renvoie 0.045 à l'étape suivante et obtient 5 558,32 AED. Sans la porte, la fonction aurait calculé une mensualité de 375 000 AED par mois (1 000 000 × 0,375), que le modèle aurait peut-être recopiée au client. Avec un appel correct dans 90 % des cas et deux relances, l'étape réussit dans 99,9 % des cas au lieu de 90 %.

### RH — une ancienneté impossible, refusée par une borne que l'API ne voit pas

Le cabinet RH qui prépare les soldes de tout compte fait lire à l'agent des contrats numérisés. Sur un contrat mal scanné, le modèle extrait une ancienneté de 75 ans pour le salarié C-5. Le schéma de `gratuite_fin_de_service` borne `annees` à 60 : la porte refuse avec `$.annees : 75 > maximum 60`, et la fonction, qui aurait rendu le plafond de 24 mois sans broncher, n'est pas appelée. L'erreur repart au modèle, qui relit le contrat ; à défaut, le dossier passe à un gestionnaire. La définition envoyée à l'API, elle, ne contient que « Contraintes : minimum=0, maximum=60. » dans la description : une indication pour le modèle, pas une garantie.

### Immobilier — deux équipes, un même nom d'outil

Une agence immobilière de Dubaï branche sur le même agent deux modules : celui de la comptabilité, qui enregistre `tva`, et celui des transactions, qui veut enregistrer un second `tva` pour les frais de transfert de la DLD, 4 % de la valeur du bien. Avec un registre qui écraserait en silence, l'outil de TVA deviendrait un calcul de frais DLD, et une commission de 50 000 AED HT recevrait 2 000 AED de « TVA » au lieu de 2 500 AED. Avec `Registre.outil`, le second enregistrement lève `ValueError` au démarrage de l'agent, avant le premier client : l'équipe renomme son outil `frais_dld`, qui rend 96 000 AED pour un appartement de 2 400 000 AED.

## Travail à faire

Toutes les commandes se lancent dans PowerShell, depuis le dossier `projet/` du palier. Si `python` ouvre le Microsoft Store, remplace-le par le chemin complet `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.

1. Ouvre `projet/agent/outils.py`. `Outil`, les trois exceptions et `Registre.__init__` sont fournis ; chaque autre méthode a sa docstring, des `# TODO` et un `raise NotImplementedError`. Lance les tests : les 46 tests des paliers 01 à 03 passent, les 12 du palier 04 échouent par `NotImplementedError`.

```text
cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\04-Registre-d-Outils\projet"
python -m unittest -v tests.test_04_outils
```

2. Code `__len__`, `__contains__` et le décorateur `outil`, puis lance `python -m unittest -v tests.test_04_outils.TestRegistre.test_le_decorateur_rend_la_fonction`.
3. Code `porte` et `appelables`, puis lance `python -m unittest -v tests.test_04_outils.TestPorte.test_le_schema_arrete_avant_la_fonction`.
4. Code `enregistrer_outils_metier` à partir du tableau des cinq outils, puis lance `python -m unittest -v tests.test_04_outils.TestPorte tests.test_04_outils.TestOutilsMetier`.
5. Code `definitions_api`, puis lance `python -m unittest -v tests.test_04_outils.TestDefinitionsApi`.
6. Code `executer_appel`, puis lance `python -m unittest -v tests.test_04_outils.TestExecuterAppel tests.test_04_outils.TestRegistre`.
7. Lance toute la suite, puis la démo :

```text
python -m unittest -v
python demo.py
```

## Critères de réussite

- `python -m unittest -v` affiche `Ran 58 tests` puis `OK` : les 46 tests des paliers 01 à 03 et les 12 tests du palier 04.
- `python demo.py` affiche exactement la sortie ci-dessous.
- Aucune variable globale dans le module : deux `Registre()` sont indépendants.
- La fonction d'un outil n'est jamais appelée avec des arguments non conformes, et `executer_appel` ne laisse sortir aucune exception.

### Sortie attendue de demo.py

```text
Palier 04 — les outils de la banque B-1, derrière leur porte
1. 5 outils : mensualite, ratio_endettement, convertir_aed_usd, gratuite_fin_de_service, tva
   définitions API strictes : True ; n_mois envoyé : {'type': 'integer', 'description': 'Contraintes : minimum=1, maximum=300.'}
2. mensualite(1 000 000 AED, 4,5 %, 300 mois) → {'mensualite_aed': 5558.32}
   ratio_endettement(6 000, 5 558,32, 40 000) → {'ratio': 0.289, 'recevable': True}
   convertir_aed_usd(5 558,32) → {'montant_usd': 1513.5}
3. n_mois="300" arrêté par le schéma, la fonction n'est pas exécutée : $.n_mois : type attendu integer, reçu string
4. tva({'montant_ht': 12000}) → is_error = False ; {"tva_aed": 600.0, "ttc_aed": 12600.0}
4. tva({'montant_ht': -5}) → is_error = True ; ArgumentsInvalides: $.montant_ht : -5 < minimum 0
4. virement({'montant_aed': 180000}) → is_error = True ; ErreurOutil: outil inconnu : virement
OK — palier 04 terminé.
```

## Pour aller plus loin

1. **Exposer le registre en serveur MCP.** Écris `tools_list(registre)` et `tools_call(registre, nom, arguments)` au format de l'étape 46. Réponse attendue : `tools_list` rend `{"tools": [...]}` avec, pour chaque outil, `name`, `description` et `inputSchema` égal au schéma **complet** (MCP n'a pas le mode strict), et `tools_call` passe par `executer_appel`, dont `is_error` devient `isError` et dont le `content` devient `[{"type": "text", "text": ...}]`.
2. **Ne pas compter les erreurs de l'agent contre l'outil.** Ajoute à `executer_appel` un compteur facultatif des échecs par outil et par type d'exception. Réponse attendue : un `collections.Counter` indexé par `(bloc.name, type(e).__name__)` ; les `ArgumentsInvalides` mesurent la qualité des appels du modèle, les autres exceptions la fiabilité de l'outil, et seules ces dernières entrent dans sa disponibilité (étape 49).
3. **Un outil idempotent.** Ajoute au registre un cache, pour qu'un même appel répété (même nom, mêmes arguments, champs dans n'importe quel ordre) ne réexécute pas la fonction. Réponse attendue : la clé `hashlib.sha256((nom + json.dumps(arguments, sort_keys=True)).encode()).hexdigest()` est identique pour `{"a": 1, "b": 2}` et `{"b": 2, "a": 1}`, et la fonction n'est appelée qu'une fois (étape 12).

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`. Ouvre seulement le fichier de l'étape qui te bloque :

- [01 — L'outil et les exceptions](<solutions/progression/01-Outil-et-exceptions.md>) : la `dataclass` `Outil` et pourquoi trois exceptions, chacune sous la bonne classe mère.
- [02 — Le registre et son décorateur](<solutions/progression/02-Registre-et-decorateur.md>) : `__len__`, `__contains__`, et un décorateur à paramètres qui contrôle le nom avant de décorer.
- [03 — La porte et les appelables](<solutions/progression/03-Porte-et-appelables.md>) : une fermeture qui valide avant d'appeler, et le piège des lambdas dans une boucle.
- [04 — Les cinq outils métier](<solutions/progression/04-Outils-metier.md>) : enregistrer des fonctions internes, avec leurs schémas et leurs arrondis.
- [05 — Les définitions pour l'API](<solutions/progression/05-Definitions-API.md>) : le mode strict, et pourquoi la porte garde le schéma complet.
- [06 — L'enveloppe d'erreur](<solutions/progression/06-Executer-appel.md>) : `executer_appel`, un `try`/`except` qui renvoie l'erreur au modèle au lieu de la laisser sortir.
- [07 — Assemblage et démo](<solutions/progression/07-Assemblage-et-demo.md>) : le module entier, tous les tests, la démo et le passage au palier 05.

La solution complète est dans `solutions/agent/outils.py` ; `solutions/demo.py` et `solutions/tests/` sont identiques à ceux de `projet/`.
