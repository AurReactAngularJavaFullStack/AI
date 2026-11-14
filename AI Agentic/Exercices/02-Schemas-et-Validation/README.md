# Palier 02 — Schémas et validation

> Palier 02 sur 12 · Précédent : [Palier 01 — Le modèle et le prompt](<../01-Modele-et-Prompt/README.md>) · Suivant : [Palier 03 — Outils métier EAU](<../03-Outils-Metier-EAU/README.md>) · Leçons à relire : [Étape 8 — Schémas : définitions et validateur](<../../03-Schemas-Outils-et-Premiere-Evaluation/08-Schemas-Definitions-Fondamentaux.md>) · [Étape 9 — Six schémas EAU](<../../03-Schemas-Outils-et-Premiere-Evaluation/09-Schemas-Exemples-Cas-Usage.md>) · [Étape 10 — Schémas par domaine](<../../03-Schemas-Outils-et-Premiere-Evaluation/10-Schemas-Applications-Domaines.md>) · [Étape 11 — Taux de validation et réparation](<../../03-Schemas-Outils-et-Premiere-Evaluation/11-Schemas-Formule-Taux-de-Validation.md>) · [Étape 77 — Projet final](<../../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Démonstrations : aucune n'est propre à ce palier ; la formule de réparation prolonge [29 — Fiabilité en série](<../../Demonstrations/01-Introduction/29_fiabilite_serie.md>)

Tu écris ici le deuxième module du paquet : `agent/schemas.py`. À la fin du palier, ton agent sait vérifier qu'une donnée produite par le modèle a la bonne forme avant d'en faire quoi que ce soit : il rend la liste exacte des écarts avec leur chemin JSON, prépare les schémas pour le mode strict de l'API, et relance le modèle avec ses erreurs quand le JSON est faux, au plus trois fois, avant de passer la main à un humain.

## Où en est l'agent

Le palier 01 a posé le port LLM : `FakeLLM` rejoue des réponses, `construire_prompt` assemble le système et le message. Mais rien ne contrôle encore ce que le modèle rend. Un modèle qui écrit `"duree_mois": "36"` (une chaîne) au lieu de `36` (un entier), ou `"revenu_mensuel_aed": true`, enverrait ces valeurs droit dans le calcul de la mensualité.

```text
  agent/
  ├── modele.py          ✓ palier 01 : Horloge, Bloc, Reponse, FakeLLM, softmax, fiabilité, prompt
  ├── schemas.py         ◄── PALIER 02 (ici) : validate, objet, mode strict, lire_et_valider, reparer
  ├── metier.py              palier 03 : calculs EAU
  ├── outils.py              palier 04 : registre d'outils (sa porte appellera validate)
  ├── boucle.py              palier 05 : boucle ReAct
  └── …                      paliers 06 à 12
```

Dans la boucle percevoir → décider → agir → observer, le schéma intervient à deux charnières.

```text
  ENTRE DÉCIDER ET AGIR (palier 04)
  modèle ──► appel d'outil, input = {"n_mois": "300"}
                     │
                     ▼
        validate(input, schéma de l'outil) ──► erreurs ──► renvoyées au modèle, l'outil n'est PAS exécuté
                     │ liste vide
                     ▼
              outil métier (palier 03)

  ENTRE OBSERVER ET RÉPONDRE (ce palier)
  modèle ──► texte JSON ──► lire_et_valider ──► erreurs ? ──► oui : reparer relance le modèle
                                                   │                (au plus max_essais essais, puis humain)
                                                   ▼ non
                                         données valides ──► suite du traitement
```

Le validateur est un garde-fou d'entrée. Pour un développeur Spring, c'est le `@Valid` d'un `@RequestBody` : la requête mal formée est refusée à la frontière, avec la liste des champs fautifs, et le service métier ne reçoit que des objets déjà valides.

## Ce que tu vas coder

- `MOTS_CLES`, `TYPES` et `NOMS_JSON` (fournis) : les onze mots-clés reconnus, la correspondance entre types JSON et types Python, et le nom JSON d'un type Python.
- `validate` : la liste des écarts entre une instance et un schéma, chacun avec son chemin JSON (`$`, `$.duree_mois`).
- `objet` : fabrique un schéma d'objet strict, où tous les champs sont obligatoires et aucun champ non prévu n'est accepté.
- `NON_STRICT` et `schema_pour_api_strict` : retire les bornes que le mode strict de l'API refuse et les recopie dans la description.
- `MOTIF_EMIRATES_ID` et `SCHEMA_DEMANDE_CREDIT` (fournis) : le schéma d'une demande de prêt personnel, écrit en toutes lettres.
- `lire_et_valider` : lit un texte JSON et le valide ; un JSON illisible devient une erreur comme une autre.
- `reparer` : la boucle de réparation, sur le port LLM du palier 01.
- `p_succes` et `essais_moyens` : la probabilité de finir avec un JSON valide, et le coût moyen en appels.

**Par rapport à l'étape 77 et à l'étape 8.** `validate` et `schema_pour_api_strict` sont ceux de la section 3 de l'étape 77, recopiés : mêmes chemins, mêmes messages, onze mots-clés, pas de tableaux ni d'énumérations, et `36.0` refusé comme entier (l'étape 8 l'accepte). `objet` vient de la section 8 de l'étape 77 ; il est rangé ici parce que c'est une fabrique de schéma, que les paliers 04, 07 et 09 réutiliseront. `SCHEMA_DEMANDE_CREDIT` est écrit explicitement, pour que tu voies le JSON Schema complet ; un test vérifie qu'il est égal à ce que rendrait `objet`. `lire_et_valider` est celui de l'étape 8, et `reparer` est sa fonction `extraire_avec_reparation`, renommée, qui compte des **essais** (`max_essais=3`) au lieu de relances (`relances_max=2`). Le motif de l'Emirates ID s'appelle ici `MOTIF_EMIRATES_ID`.

## Rappel de cours

### Ce qu'est une validation (étape 8)

Un schéma JSON est un contrat sur la forme d'une donnée. Valider une instance x contre un schéma S, c'est produire la liste de tous les écarts ; l'instance est conforme si et seulement si cette liste est vide :

$$
x \text{ conforme à } S \iff \mathrm{validate}(x, S) = [\;]
$$

Chaque erreur porte un chemin JSON : `$` désigne la racine, `$.duree_mois` le champ `duree_mois` de la racine. La validation est récursive : un champ d'objet est validé contre son propre sous-schéma, avec le chemin prolongé. Un schéma ne dit rien de la vérité d'une donnée : un montant de 150 000 AED peut être valide et faux.

### La boucle de réparation (étapes 8 et 11)

Quand la validation échoue, l'agent renvoie les erreurs au modèle et lui redemande le JSON. Il fait au plus R relances, donc au plus R + 1 essais, puis il passe la main à un humain. Si chaque essai réussit avec la même probabilité p, indépendamment des autres, la demande échoue seulement si les R + 1 essais échouent tous :

$$
P_{\text{succ}}(R) = 1 - (1 - p)^{R+1}
$$

L'essai numéro i + 1 n'a lieu que si les i premiers ont échoué, ce qui arrive avec la probabilité (1 − p)ⁱ. En additionnant ces probabilités (formule des queues de l'étape 11), on obtient le nombre moyen d'essais :

$$
\mathbb{E}[A] = \sum_{i=0}^{R} (1 - p)^i = 1 + (1 - p) + \cdots + (1 - p)^R = \frac{P_{\text{succ}}(R)}{p}
$$

La dernière égalité vient de la somme géométrique : en multipliant la somme par (1 − p) et en retranchant, presque tous les termes se simplifient, et il reste p fois la somme égale à 1 − (1 − p)^(R+1).

Le gain d'une relance de plus décroît très vite, ce qui justifie R = 2 :

$$
P_{\text{succ}}(R + 1) - P_{\text{succ}}(R) = p\,(1 - p)^{R+1}
$$

Avec p = 0,9 : la première relance fait passer de 0,9 à 0,99, la deuxième de 0,99 à 0,999, la troisième n'apporterait plus que 0,0009.

Dans le code, la boucle compte des essais, pas des relances :

$$
\text{max\_essais} = R + 1
$$

### Les symboles, un par un

$$
x
$$

**x** : l'instance, la donnée à valider (ici le dictionnaire produit par `json.loads`).

$$
S
$$

**S** : le schéma, lui-même un dictionnaire JSON (`{"type": "integer", "minimum": 12}`).

$$
p
$$

**p** : la probabilité qu'un essai du modèle rende un JSON valide ; on exige 0 < p ≤ 1.

$$
1 - p
$$

**1 − p** : la probabilité qu'un essai échoue.

$$
R
$$

**R** : le nombre maximal de relances, un entier ≥ 0 ; R = 0 veut dire « pas de réparation ».

$$
R + 1
$$

**R + 1** : le nombre maximal d'essais, le paramètre `max_essais` de `reparer`.

$$
A
$$

**A** : le nombre d'essais réellement faits pour une demande, entre 1 et R + 1.

$$
\mathbb{E}[A]
$$

**𝔼[A]** : sa moyenne sur un grand nombre de demandes, c'est-à-dire le coût moyen en appels au modèle.

$$
P_{\text{succ}}(R)
$$

**P_succ(R)** : la probabilité qu'une demande finisse avec un JSON valide quand on autorise R relances.

## Spécification

### MOTS_CLES, TYPES et NOMS_JSON (fournis)

```python
# [extrait] spécification
MOTS_CLES = {"type", "properties", "required", "additionalProperties", "minimum", "maximum", "exclusiveMinimum",
             "minLength", "maxLength", "pattern", "description"}
TYPES = {"object": (dict,), "string": (str,), "number": (int, float), "integer": (int,)}
NOMS_JSON = {bool: "boolean", int: "integer", float: "number", str: "string", list: "array", dict: "object"}
```

`TYPES` dit quelles classes Python acceptent un type JSON : un `number` JSON peut être un `int` ou un `float` Python, un `integer` seulement un `int`. `NOMS_JSON` sert dans les messages : `NOMS_JSON[type(x)]`, et `"null"` pour un type absent du dictionnaire (`None`).

### validate

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`validate(instance, schema, path)`** — Cette fonction doit être le douanier qui inspecte une donnée venue du modèle, pièce par pièce, contre le règlement qu'est le schéma : elle reçoit l'instance à examiner, le schéma sous forme de dictionnaire et le chemin JSON du nœud courant, `"$"` par défaut pour la racine, et renvoie la liste des écarts trouvés, vide si l'instance est conforme. Elle lève `ValueError` dès que le schéma contient un mot-clé absent de `MOTS_CLES`, comme `multipleOf`, et elle doit traiter un booléen comme un booléen, jamais comme l'entier 1, même si Python le range parmi les `int`. Chaque message porte le chemin de l'écart, au caractère près : la chaîne `"300"` à la place d'une durée produit une seule erreur de type, sans test des bornes, et la demande correcte contre `SCHEMA_DEMANDE_CREDIT` donne la liste vide.

```python
# [extrait] spécification
def validate(instance, schema: dict, path: str = "$") -> list[str]: ...
```

Rend la liste des écarts, dans cet ordre :

1. Si le schéma contient un mot-clé absent de `MOTS_CLES`, lever `ValueError("mots-clés non pris en charge : [...]")` avec la liste triée des mots inconnus : on refuse un schéma qu'on ne sait pas appliquer plutôt que d'ignorer une contrainte en silence.
2. Si le schéma a un `type` et que l'instance n'est pas d'une classe de `TYPES[type]`, **ou si c'est un booléen**, rendre aussitôt une liste d'une seule erreur : le reste du nœud n'est pas examiné.
3. Pour un nombre (qui n'est pas un booléen) : NaN ou infini rendent aussitôt une erreur ; puis `minimum`, `maximum` (bornes incluses) et `exclusiveMinimum` (borne exclue), dans cet ordre.
4. Pour une chaîne : `minLength`, `maxLength`, puis `pattern`, cherché avec `re.search`.
5. Pour un objet : d'abord un message par champ de `required` absent, dans l'ordre de `required` ; puis, pour chaque champ de l'instance, dans l'ordre de l'instance, la validation récursive contre son sous-schéma avec le chemin `path + "." + champ`, ou, si le champ n'est pas décrit et que `additionalProperties` vaut `False`, une erreur « champ non prévu ».

Les messages, au caractère près (P est le chemin) :

| Écart | Message |
| --- | --- |
| type faux | `P : type attendu integer, reçu string` |
| nombre non fini | `P : nombre non fini (nan), interdit en JSON` |
| sous le minimum | `P : 0 < minimum 1` |
| au-dessus du maximum | `P : 301 > maximum 300` |
| borne exclue | `P : 0 doit être > 0` |
| chaîne trop courte | `P : longueur 0 < minLength 1` |
| chaîne trop longue | `P : longueur 4 > maxLength 3` |
| motif | `P : '' ne respecte pas le motif ^[A-Z]+$` |
| champ obligatoire absent | `P : champ obligatoire absent « emirates_id »` |
| champ non prévu | `P : champ non prévu « commentaire »` |

Dans ces messages, les nombres et les bornes sont écrits tels que Python les affiche (`0`, `301`, `nan`), et la chaîne testée par un motif est affichée avec ses apostrophes, c'est-à-dire sa représentation `repr` : la chaîne vide s'écrit `''`.

**Exemple 1 : le type et le chemin.** Le schéma `objet({"n_mois": {"type": "integer", "minimum": 1, "maximum": 300}})` reçoit `{"n_mois": "300"}`. La racine est bien un objet ; le champ `n_mois` est présent ; on descend avec le chemin `$.n_mois` ; `"300"` est une chaîne, pas un `int` : une seule erreur, `$.n_mois : type attendu integer, reçu string`, et les bornes ne sont pas testées (test `TestValidateTypes.test_type_faux_avec_chemin`).

**Exemple 2 : le booléen.** En Python, `isinstance(True, int)` est vrai et `True + 1` vaut 2. Sans contrôle explicite, `true` passerait pour l'entier 1. `validate(True, {"type": "integer"})` rend donc `$ : type attendu integer, reçu boolean`, et `validate(None, {"type": "number"})` rend `$ : type attendu number, reçu null` (test `TestValidateTypes.test_booleen_n_est_pas_un_entier`). `36.0` est un `float` : contre `integer`, il donne `reçu number` ; `float("nan")` contre `number` donne `$ : nombre non fini (nan), interdit en JSON` (test `TestValidateTypes.test_decimal_refuse_comme_entier_et_nan_refuse`). Un schéma `{"type": "integer", "multipleOf": 5}` lève `ValueError` (test `TestValidateTypes.test_mot_cle_inconnu_refuse`).

**Exemple 3 : les bornes.** Avec N = `{"type": "integer", "minimum": 1, "maximum": 300}` : 301 donne `$ : 301 > maximum 300`, 0 donne `$ : 0 < minimum 1`, 300 donne la liste vide (borne incluse). Sans `type`, `validate(0, {"exclusiveMinimum": 0})` rend `$ : 0 doit être > 0`, parce que 0 n'est pas strictement supérieur à 0 (test `TestValidateContraintes.test_bornes_numeriques`).

**Exemple 4 : les chaînes.** Avec `minLength` 1, `maxLength` 3 et le motif `^[A-Z]+$` : la chaîne vide donne deux erreurs, la longueur 0 < 1 puis le motif (au moins une majuscule est exigée) ; `"ABCD"` n'en donne qu'une, la longueur 4 > 3, puisque le motif est respecté (test `TestValidateContraintes.test_chaines`).

**Exemple 5 : un objet complet.** On part de la demande correcte `{"montant_aed": 150000, "duree_mois": 36, "revenu_mensuel_aed": 25000, "emirates_id": "784-1990-1234567-1"}`, on met la durée à 6, on ajoute `"commentaire": "urgent"` et on retire `emirates_id`. Contre `SCHEMA_DEMANDE_CREDIT`, la fonction examine d'abord `required` : `emirates_id` manque. Puis les champs de l'instance, dans l'ordre : `montant_aed` (150 000 > 0, conforme), `duree_mois` (6 < 12), `revenu_mensuel_aed` (conforme), `commentaire` (non décrit, et `additionalProperties` vaut `False`). Résultat, dans cet ordre : `$ : champ obligatoire absent « emirates_id »`, `$.duree_mois : 6 < minimum 12`, `$ : champ non prévu « commentaire »`. La demande correcte donne la liste vide (test `TestValidateContraintes.test_objet_champs_absents_et_non_prevus`).

### objet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`objet(proprietes)`** — Cette petite fabrique doit agir comme un notaire qui transforme une simple liste de clauses en contrat fermé : elle reçoit le dictionnaire des propriétés, chaque nom de champ associé à son sous-schéma, et renvoie un schéma d'objet complet dont le `type` vaut `"object"`, dont `properties` reprend ce dictionnaire, dont `required` liste tous les noms de champs dans leur ordre, et dont `additionalProperties` vaut `False`. Tout champ décrit devient ainsi obligatoire et tout champ non décrit est interdit ; appliquée aux propriétés de `SCHEMA_DEMANDE_CREDIT`, elle doit redonner exactement ce schéma.

```python
# [extrait] spécification
def objet(proprietes: dict) -> dict: ...
```

Rend `{"type": "object", "properties": proprietes, "required": [noms des champs, dans l'ordre], "additionalProperties": False}`.

**Exemple.** `objet({"x": {"type": "number"}})` vaut `{"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"], "additionalProperties": False}`, et `objet(SCHEMA_DEMANDE_CREDIT["properties"])` est égal à `SCHEMA_DEMANDE_CREDIT` (test `TestSchemaStrict.test_objet`).

### schema_pour_api_strict

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`schema_pour_api_strict(schema)`** — Cette fonction doit jouer le traducteur qui adapte un règlement trop détaillé au formulaire plus sommaire qu'accepte le guichet de l'API en mode strict : elle reçoit un schéma et renvoie une copie où, à chaque niveau, les cinq mots-clés de `NON_STRICT` sont retirés puis recopiés dans la description sous la forme « Contraintes : k=v, k=v. », à la suite d'une éventuelle description existante. Les sous-schémas de `properties` sont traités de la même manière, et le schéma reçu ne doit jamais être modifié. Le sous-schéma d'une durée bornée de 1 à 300 doit ainsi devenir un entier dont la description dit « Contraintes : minimum=1, maximum=300. » ; c'est pourquoi une durée de 6 mois passe ce schéma strict mais reste refusée par la validation locale.

```python
# [extrait] spécification
NON_STRICT = ("minimum", "maximum", "exclusiveMinimum", "minLength", "maxLength")


def schema_pour_api_strict(schema: dict) -> dict: ...
```

En mode strict, l'API garantit que les arguments respectent le schéma (types, champs obligatoires, aucun champ en trop), mais elle refuse un schéma qui contient des bornes numériques ou des longueurs. La fonction rend une **copie** du schéma où, à chaque niveau, les mots-clés de `NON_STRICT` sont retirés et recopiés dans la description, sous la forme « Contraintes : k=v, k=v. », dans l'ordre où ils apparaissent dans le schéma. S'il existait déjà une description, ce texte la suit, séparé par une espace ; sinon, la description commence directement par « Contraintes ». Les sous-schémas de `properties` sont traités récursivement. Le schéma reçu n'est jamais modifié.

**Exemple.** Le sous-schéma `{"type": "integer", "minimum": 1, "maximum": 300}` devient `{"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}`, et le JSON du schéma rendu ne contient plus aucun des cinq mots-clés (test `TestSchemaStrict.test_bornes_retirees_et_recopiees`). Conséquence : une demande de 6 mois passe le schéma strict, mais pas le schéma local, qui rend `$.duree_mois : 6 < minimum 12`. La validation locale reste obligatoire, même en mode strict (test `TestSchemaStrict.test_la_validation_locale_reste_necessaire`).

### MOTIF_EMIRATES_ID et SCHEMA_DEMANDE_CREDIT (fournis)

```python
# [extrait] spécification
MOTIF_EMIRATES_ID = "^784-[0-9]{4}-[0-9]{7}-[0-9]$"
SCHEMA_DEMANDE_CREDIT = {"type": "object", "properties": {...}, "required": [...], "additionalProperties": False}
```

Quatre champs obligatoires : un montant strictement positif en AED, une durée entière de 12 à 300 mois, un revenu mensuel strictement positif en AED, et un Emirates ID au format `784-AAAA-NNNNNNN-C`. Le motif ne vérifie que le format (15 chiffres commençant par 784, avec ses tirets), pas l'existence du numéro. Les bornes de durée sont illustratives ; le plafond d'endettement de la CBUAE (50 % du revenu) est une règle entre deux champs, vérifiée par un outil au palier 03.

### lire_et_valider

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`lire_et_valider(texte_llm, schema)`** — Cette fonction doit être le greffier qui reçoit la copie rendue par le modèle et refuse de l'enregistrer tant qu'elle n'est pas lisible et conforme : elle reçoit le texte brut produit par le modèle et le schéma attendu, tente de le lire avec `json.loads`, et renvoie toujours un couple. Un texte illisible donne `None` accompagné d'une erreur unique qui cite le message et la position de l'exception ; un texte lisible est validé, et l'on obtient soit les données avec une liste vide, soit `None` avec la liste des écarts. Elle ne rend jamais de données invalides : un JSON entouré d'un bloc de code Markdown doit donner l'erreur « JSON illisible (Expecting value, position 0) ».

```python
# [extrait] spécification
def lire_et_valider(texte_llm: str, schema: dict) -> tuple[dict | None, list[str]]: ...
```

Lit le texte avec `json.loads`. Un texte illisible rend `(None, ["$ : JSON illisible (MESSAGE, position N)"])`, avec le message et la position de l'exception. Sinon, valide : rend `(données, [])` si la liste est vide, `(None, erreurs)` sinon. On ne rend jamais des données invalides.

**Exemple.** Un modèle qui entoure son JSON d'un bloc de code Markdown (trois accents graves, `json`, puis le JSON) ne produit pas du JSON : le premier caractère n'est pas une valeur, et la fonction rend `(None, ["$ : JSON illisible (Expecting value, position 0)"])` (test `TestReparation.test_json_dans_un_bloc_de_code`).

### reparer

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`reparer(llm, schema, demande, max_essais)`** — Cette fonction doit mener la négociation patiente d'un chef de bureau qui renvoie un formulaire mal rempli à son auteur en soulignant chaque case fautive : elle reçoit le modèle, le schéma, la demande de l'utilisateur et le nombre maximal d'essais, 3 par défaut, et lève `ValueError` si ce nombre est inférieur à 1. À chaque essai, numéroté à partir de 1, elle interroge le modèle avec un système qui contient le schéma en JSON, s'arrête aussitôt sur un `"refusal"` ou un `"max_tokens"`, lit et valide sinon le texte de la réponse, et, en cas d'écarts, ajoute à l'historique la réponse fautive puis un message qui liste les erreurs. Elle renvoie un dictionnaire de quatre clés, `statut`, `donnees`, `essais` et `erreurs` ; une durée écrite `"36"` doit être corrigée au deuxième essai, après deux appels au modèle, et trois montants nuls de suite doivent donner le statut « echec ».

```python
# [extrait] spécification
def reparer(llm, schema: dict, demande: str, max_essais: int = 3) -> dict: ...
```

- `max_essais < 1` lève `ValueError`.
- Le système vaut `"Réponds uniquement par un objet JSON conforme à ce schéma : "` suivi du schéma en JSON (`json.dumps(schema, ensure_ascii=False)`) ; l'historique commence par un message `user` qui contient la demande.
- À chaque essai, numéroté à partir de 1 : appel `llm.create(system=..., messages=..., tools=[])`. Si `stop_reason` vaut `"refusal"` ou `"max_tokens"`, on rend **tout de suite** ce statut, sans lire le contenu : un refus ne se répare pas. Sinon, on concatène le texte des blocs de type `"text"`, on appelle `lire_et_valider`, et l'on ajoute la liste d'erreurs de l'essai à l'historique des erreurs. Si elle est vide, on rend `"valide"`. Sinon, on ajoute à `messages` la réponse fautive (rôle `assistant`, contenu recopié tel quel), puis un message `user` : `"Ta réponse ne respecte pas le schéma :\n"`, les erreurs une par ligne, et `"\nRenvoie uniquement l'objet JSON corrigé."`.
- Après `max_essais` essais ratés, statut `"echec"`.

Le résultat est toujours un dictionnaire de quatre clés : `statut`, `donnees` (`None` sauf si valide), `essais` (le numéro du dernier essai fait) et `erreurs` (une liste d'erreurs par essai **lu** : un refus n'en ajoute pas).

**Exemple.** Le faux modèle rend d'abord la demande correcte avec `"duree_mois": "36"`, puis la demande correcte. Essai 1 : une erreur, `$.duree_mois : type attendu integer, reçu string`, renvoyée au modèle dans le dernier message ; essai 2 : liste vide. Résultat : statut `"valide"`, 2 essais, 2 appels au modèle, les données correctes, et `erreurs` vaut `[["$.duree_mois : type attendu integer, reçu string"], []]` (test `TestReparation.test_une_relance_suffit`). Trois réponses avec un montant nul donnent `"echec"`, 3 essais, 3 appels, `donnees` à `None` (test `TestReparation.test_echec_apres_max_essais`). Un refus donne `"refusal"`, 1 essai et aucune liste d'erreurs (test `TestReparation.test_refus_traite_avant_le_contenu`).

### p_succes et essais_moyens

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`p_succes(p, relances)`** — Cette fonction doit faire le calcul d'un assureur qui se demande combien de dossiers finiront bien si l'on accorde au modèle quelques secondes chances : elle reçoit la probabilité p qu'un essai rende un JSON valide et le nombre R de relances permises, lève `ValueError` si p n'est pas dans ]0, 1] ou si R est négatif, et renvoie la probabilité qu'au moins un des R + 1 essais réussisse, c'est-à-dire 1 moins (1 − p) élevé à la puissance R + 1. Avec p = 0,9 et deux relances, elle doit donner 0,999, chiffre qui justifie, dans la boucle de réparation, l'arrêt après trois essais.

**`essais_moyens(p, relances)`** — Celle-ci tient le registre du comptable qui veut savoir combien d'appels au modèle coûte, en moyenne, une demande : elle reçoit les mêmes p et R, lève les mêmes `ValueError`, et doit additionner les R + 1 termes 1, (1 − p), (1 − p)², jusqu'à (1 − p) puissance R, sans recourir à la forme fermée, puisque l'essai numéro i + 1 n'a lieu que si les i premiers ont échoué. Pour p = 0,9 et deux relances, elle doit renvoyer 1 + 0,1 + 0,01 = 1,11, qui vaut aussi 0,999 divisé par 0,9 : le test vérifie cette identité avec `p_succes`.

```python
# [extrait] spécification
def p_succes(p: float, relances: int) -> float: ...
def essais_moyens(p: float, relances: int) -> float: ...
```

Les deux formules du rappel de cours. Les deux fonctions lèvent `ValueError` si p n'est pas dans l'intervalle ]0, 1] ou si `relances` est négatif. `essais_moyens` additionne les R + 1 termes, sans utiliser la forme fermée.

**Exemple.** p = 0,9 et R = 2 relances :

$$
P_{\text{succ}}(2) = 1 - 0{,}1^3 = 1 - 0{,}001 = 0{,}999, \qquad \mathbb{E}[A] = 1 + 0{,}1 + 0{,}01 = 1{,}11 = \frac{0{,}999}{0{,}9}
$$

Test `TestReparation.test_probabilites`, qui vérifie aussi l'identité entre les deux fonctions et refuse p = 0, p = 1,2 et R = −1.

## Squelette algorithmique

```text
ALGORITHME Valider(x, S, chemin)
ENTRÉES : instance x, schéma S, chemin (racine : "$")
SORTIE  : liste d'erreurs (vide si x est conforme)
  SI S contient un mot-clé inconnu ALORS lever ValueError
  SI S impose un type ET (x est un booléen OU x n'est pas de ce type) ALORS
      RETOURNER [chemin : type attendu, type reçu]
  erreurs ← []
  SI x est un nombre ALORS
      SI x n'est pas fini ALORS RETOURNER [chemin : nombre non fini]
      tester minimum, maximum, exclusiveMinimum
  SINON SI x est une chaîne ALORS
      tester minLength, maxLength, motif
  SINON SI x est un objet ALORS
      POUR CHAQUE champ c de S.required absent de x : ajouter « champ obligatoire absent c »
      POUR CHAQUE (c, v) de x, dans l'ordre de x FAIRE
          SI c est décrit dans S.properties ALORS erreurs ← erreurs + Valider(v, S.properties[c], chemin.c)
          SINON SI S interdit les champs en plus ALORS ajouter « champ non prévu c »
  RETOURNER erreurs

ALGORITHME SchémaStrict(S)
  copie ← S sans les bornes ni properties
  SI S a des properties ALORS copie.properties[c] ← SchémaStrict(S.properties[c]) pour chaque c
  SI S avait des bornes ALORS ajouter « Contraintes : k=v, … » à la description de la copie
  RETOURNER copie

ALGORITHME Réparer(modèle, S, demande, M essais au plus)
  messages ← [demande]
  POUR essai DE 1 À M FAIRE
      réponse ← modèle(système avec S, messages)
      SI réponse.arrêt ∈ {refus, tronquée} ALORS RETOURNER (arrêt, aucune donnée, essai)
      (données, erreurs) ← LireEtValider(texte de la réponse, S)
      SI erreurs est vide ALORS RETOURNER (« valide », données, essai)
      ajouter à messages la réponse fautive, puis les erreurs avec leurs chemins
  FIN POUR
  RETOURNER (« echec », aucune donnée, M)                      (escalade vers un humain)
```

**Complexité.** `validate` visite chaque nœud de l'instance une fois, avec au plus onze mots-clés par nœud : O(n) pour une instance de n nœuds, hors coût des expressions régulières, qui dépend du motif. `schema_pour_api_strict` est linéaire en la taille du schéma. `reparer` fait au plus M appels au modèle, en moyenne `essais_moyens(p, M - 1)`, soit 1,11 appel pour p = 0,9 et M = 3 ; l'historique grossit d'une réponse et d'une liste d'erreurs à chaque relance, ce qui alourdit chaque appel suivant.

**Du squelette au code.** `Valider` correspond à `validate`, dont les dictionnaires `TYPES` et `NOMS_JSON` font le contrôle de type et le nom du type reçu. `SchémaStrict` correspond à `schema_pour_api_strict`, avec la liste `NON_STRICT` des bornes retirées. `Réparer` correspond à `reparer`, dont le paramètre `max_essais` est M ; `LireEtValider` correspond à `lire_et_valider`. Les deux formules de la boucle sont `p_succes` et `essais_moyens`.

## Cas d'usage aux Émirats

### Banque — une demande de prêt extraite d'un courriel

La banque B-1, à Dubaï, reçoit chaque jour environ 2 000 demandes de prêt personnel par courriel (volume illustratif), que son agent transforme en objet `SCHEMA_DEMANDE_CREDIT` avant tout calcul. Le client C-2 écrit « 150 000 AED sur 36 mois » ; le modèle rend `"duree_mois": "36"`. `validate` répond `$.duree_mois : type attendu integer, reçu string`, `reparer` renvoie ce chemin au modèle, qui corrige au deuxième essai. Si un essai réussit 9 fois sur 10 (valeur illustrative), deux relances donnent 99,9 % de demandes valides pour 1,11 appel en moyenne : 2 000 × 1,11 = 2 220 appels par jour, et 2 000 × 0,001 = 2 dossiers par jour qui partent en revue humaine. Sans schéma, la chaîne `"36"` irait jusqu'au calcul de la mensualité, qui planterait, ou pire, calculerait sur une valeur mal lue.

### Immobilier — un revenu « vrai » qui vaudrait 1 AED

Un agent de pré-qualification pour l'achat d'un appartement off-plan à Dubaï lit le revenu mensuel dans un formulaire. Un modèle qui écrit `"revenu_mensuel_aed": true` produit une donnée que Python accepte comme l'entier 1, puisque `isinstance(True, int)` est vrai. Sans le contrôle explicite du booléen, l'outil de ratio diviserait les mensualités par un revenu de 1 AED, et le dossier serait déclaré non recevable sans que personne sache pourquoi. Avec lui, l'erreur `$.revenu_mensuel_aed : type attendu number, reçu boolean` repart vers le modèle, comme dans la démo de ce palier.

### Financement automobile — le mode strict ne remplace pas la validation locale

Un concessionnaire de Sharjah propose à ses clients un crédit auto instruit par l'agent de la banque B-1. L'outil de simulation est déclaré au modèle en mode strict : l'API garantit alors que chaque appel a les bons champs et les bons types. Mais elle refuse un schéma qui contient des bornes : `schema_pour_api_strict` retire `minimum=12` et `maximum=300` de la durée et les recopie dans la description, que le modèle lit. Un appel avec une durée de 6 mois passe donc le contrôle de l'API ; c'est la validation locale, dans la porte de l'outil (palier 04), qui le refuse avec `$.duree_mois : 6 < minimum 12`. Le même raisonnement vaut pour l'Emirates ID du client : le motif `^784-[0-9]{4}-[0-9]{7}-[0-9]$` rejette `784199012345671` écrit sans tirets, et la réparation demande au modèle de le reformater avant que le dossier parte chez l'analyste.

## Travail à faire

1. Ouvre `projet/agent/schemas.py`. Lis les constantes fournies (`MOTS_CLES`, `TYPES`, `NOMS_JSON`, `NON_STRICT`, `MOTIF_EMIRATES_ID`, `SCHEMA_DEMANDE_CREDIT`), les docstrings et les `# TODO`.
2. Lance les tests. Les 17 tests du palier 01 passent déjà (le module `modele.py` est fourni complet) ; les 15 tests du palier 02 échouent tous par `NotImplementedError`.

   ```powershell
   cd "C:\Users\aur95\Documents\AI\AI Agentic\Exercices\02-Schemas-et-Validation\projet"
   python -m unittest -v tests.test_02_schemas
   ```

   Si `python` ouvre le Microsoft Store, remplace-le par `& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe"`.
3. Code `validate` en trois temps : le mot-clé inconnu et le type ; puis les nombres et les chaînes ; puis les objets. Écris `objet` en même temps que la partie objets. Lance ensuite `python -m unittest -v tests.test_02_schemas.TestValidateTypes tests.test_02_schemas.TestValidateContraintes` : 7 tests verts.
4. Code `schema_pour_api_strict`, puis lance `python -m unittest -v tests.test_02_schemas.TestSchemaStrict` : 3 tests verts.
5. Code `lire_et_valider`, `reparer`, `p_succes` et `essais_moyens`, puis lance `python -m unittest -v tests.test_02_schemas.TestReparation` : 5 tests verts.
6. Lance toute la suite, puis la démo :

   ```powershell
   python -m unittest -v
   python demo.py
   ```

## Critères de réussite

- `python -m unittest -v`, lancé depuis `projet/`, affiche `Ran 32 tests` puis `OK` (17 tests du palier 01, 15 du palier 02).
- `python demo.py` affiche exactement la sortie ci-dessous et se termine par `OK — palier 02 terminé.`
- Tu sais expliquer pourquoi un booléen doit être refusé comme nombre, pourquoi un type faux arrête la validation du nœud, et pourquoi la validation locale reste nécessaire en mode strict.

### Sortie attendue de demo.py

```text
Palier 02 — demande de prêt personnel du client C-2 (150 000 AED sur 36 mois)
1. Demande mal formée, erreurs avec leur chemin JSON :
   $ : champ obligatoire absent « emirates_id »
   $.montant_aed : 0 doit être > 0
   $.duree_mois : type attendu integer, reçu string
   $.revenu_mensuel_aed : type attendu number, reçu boolean
   $ : champ non prévu « commentaire »
   demande correcte : []
2. Schéma strict pour l'API, duree_mois : {'type': 'integer', 'description': 'Contraintes : minimum=12, maximum=300.'}
   6 mois passe le schéma strict : True ; le schéma local le refuse : ['$.duree_mois : 6 < minimum 12']
3. Réparation : essai 1 → ['$.duree_mois : type attendu integer, reçu string']
   statut valide en 2 essais, 2 appels au modèle
4. Trois essais ratés : statut echec → le dossier part en revue humaine
   un refus s'arrête au premier essai : statut refusal, essais 1
5. p = 0.9 par essai, 2 relances : succès 0.999, 1.11 appels en moyenne
OK — palier 02 terminé.
```

## Pour aller plus loin

**Défi 1 — le mot-clé `enum`.** Ajoute `enum` à `MOTS_CLES` et à `validate`, pour qu'un type de prêt hors de la liste `["hypothecaire", "personnel"]` soit refusé. Réponse attendue : un test `if "enum" in schema and instance not in schema["enum"]`, placé avant les branches par type, et un message comme `$.type_pret : 'perso' hors de ['hypothecaire', 'personnel']` ; pense aussi à `NON_STRICT`, que `enum` ne doit pas rejoindre, puisque le mode strict l'accepte.

**Défi 2 — combien de relances pour 99,99 % ?** Écris `relances_min(p, cible)`. Réponse attendue : pour p = 0,9, il faut 3 relances, car 1 − 0,1⁴ = 0,9999 ; attention, la formule de l'étape 11 calcule ln(0,0001) / ln(0,1), qui vaut 4,000000000000048 en flottants, et son arrondi supérieur donnerait une relance de trop : on vérifie avec `p_succes`.

**Défi 3 — les tableaux.** Ajoute `items` pour valider une liste de garanties, avec des chemins comme `$.garanties[1]`. Réponse attendue : une branche `elif isinstance(instance, list)` qui valide chaque élément contre `schema["items"]` avec le chemin `f"{path}[{i}]"`, et `"array": (list,)` dans `TYPES`.

## Si tu bloques

La solution est construite pas à pas dans `solutions/progression/`, un fichier par étape :

- [01 — Le contrôle de type](<solutions/progression/01-Controle-de-type.md>) : les constantes, le mot-clé inconnu, le piège du booléen, l'arrêt sur un type faux.
- [02 — Nombres et chaînes](<solutions/progression/02-Nombres-et-chaines.md>) : NaN, les bornes, les longueurs et le motif.
- [03 — Objets et récursion](<solutions/progression/03-Objets-et-recursion.md>) : champs obligatoires, chemins JSON, champs non prévus, `objet` et le schéma de la demande de crédit.
- [04 — Le schéma strict pour l'API](<solutions/progression/04-Schema-strict-pour-l-API.md>) : retirer les bornes sans les perdre.
- [05 — Lire puis valider](<solutions/progression/05-Lire-et-valider.md>) : un JSON illisible devient une erreur comme une autre.
- [06 — La boucle de réparation](<solutions/progression/06-Boucle-de-reparation.md>) : `reparer` sur le faux modèle du palier 01.
- [07 — Les probabilités de la réparation](<solutions/progression/07-Probabilites-de-reparation.md>) : `p_succes` et `essais_moyens`.
- [08 — Assemblage et vérification](<solutions/progression/08-Assemblage-et-verification.md>) : le module complet, les 32 tests, la démo et le passage au palier 03.

La solution entière est dans `solutions/agent/schemas.py` ; `solutions/` contient aussi les tests et la démo, identiques à ceux de `projet/`.
