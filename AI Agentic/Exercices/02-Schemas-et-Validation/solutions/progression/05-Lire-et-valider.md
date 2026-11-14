# Étape 5 — Lire puis valider

> Palier 02, étape 5 sur 8 · Précédent : [Étape 4 — Le schéma strict pour l'API](<04-Schema-strict-pour-l-API.md>) · Suivant : [Étape 6 — La boucle de réparation](<06-Boucle-de-reparation.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `lire_et_valider`, qui transforme le texte rendu par le modèle en données validées, ou en liste d'erreurs. Le test `test_json_dans_un_bloc_de_code` passe à la fin.

## Comment raisonner

`validate` travaille sur des objets Python. Or le modèle ne rend pas des objets : il rend du **texte**, qui est censé être du JSON. Il faut donc deux opérations à la suite, lire (`json.loads`) puis valider, et chacune peut échouer. La question de conception est : que fait-on quand la **lecture** échoue ?

Si l'on laisse passer l'exception `json.JSONDecodeError`, l'appelant (la boucle de réparation de l'étape 6) devra traiter deux sortes d'échec : une exception pour un texte illisible, une liste d'erreurs pour un JSON mal formé. Or, pour lui, c'est la même situation : le modèle doit recommencer, et il faut lui dire pourquoi. On **unifie** donc : un JSON illisible devient une erreur de validation comme une autre, à la racine `$`, avec le message et la position du problème.

On fixe ensuite la forme du résultat : un couple `(données, erreurs)`. Les données ne sont rendues que si la liste d'erreurs est vide ; sinon elles valent `None`. Ainsi, un appelant pressé qui ne regarderait que les données ne peut jamais utiliser une donnée invalide.

## La fonction

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`lire_et_valider(texte_llm, schema)`** — Cette fonction est le greffier qui reçoit la copie rendue par le modèle et refuse de la classer tant qu'elle n'est ni lisible ni conforme : elle reçoit le texte brut et le schéma, tente de le lire avec `json.loads`, et, si la lecture échoue, n'attrape que `json.JSONDecodeError` pour renvoyer `None` avec une erreur unique à la racine qui cite le message et la position de l'exception. Si la lecture réussit, elle appelle `validate` et renvoie le couple formé des données, ou de `None` dès qu'il y a au moins une erreur, et de la liste des erreurs. Un texte qui commence par un accent grave donne « Expecting value, position 0 », une virgule finale donne la position 17, et la boucle de réparation n'aura plus qu'une seule sorte d'échec à traiter.

```python
# [extrait] agent/schemas.py
def lire_et_valider(texte_llm: str, schema: dict) -> tuple[dict | None, list[str]]:
    """`json.loads` puis `validate` : rend (données, []) si tout va bien, (None, erreurs) sinon.

    Exemple : un JSON entouré d'un bloc de code Markdown n'est pas du JSON et donne
    (None, ["$ : JSON illisible (Expecting value, position 0)"]).
    """
    try:
        donnees = json.loads(texte_llm)
    except json.JSONDecodeError as e:
        return None, [f"$ : JSON illisible ({e.msg}, position {e.pos})"]
    erreurs = validate(donnees, schema)
    return (None if erreurs else donnees), erreurs
```

**L'annotation de retour, `tuple[dict | None, list[str]]`.** Un couple dont le premier élément est un dictionnaire ou `None`, et le second une liste de chaînes. La barre verticale entre deux types (Python 3.10 et plus) se lit « ou » ; c'est l'équivalent d'un `Optional<Map<...>>` en Java, sans l'objet qui l'enveloppe.

**`try: donnees = json.loads(texte_llm)`.** `json.loads` transforme un texte JSON en objets Python : objet JSON en `dict`, tableau en `list`, nombre en `int` ou `float`, `true` en `True`, `null` en `None`. C'est le `objectMapper.readValue(texte, Map.class)` de Jackson.

**`except json.JSONDecodeError as e:`** On n'attrape **que** l'erreur de lecture, pas `Exception` : une autre erreur (un bug dans notre code) doit continuer à remonter. L'exception porte deux attributs utiles : `e.msg`, la description (`Expecting value`, `Illegal trailing comma before end of object`…) et `e.pos`, la position du caractère fautif dans le texte. On les recopie dans le message, pour que le modèle sache où regarder.

**`erreurs = validate(donnees, schema)`.** La lecture a réussi : on valide. Attention, `json.loads` peut rendre autre chose qu'un dictionnaire (un nombre, une liste) si le modèle a répondu par `42` ou par `[...]` ; c'est `validate` qui le refusera, grâce au `"type": "object"` du schéma.

**`return (None if erreurs else donnees), erreurs`.** L'expression conditionnelle `a if condition else b` est l'opérateur ternaire de Python (`condition ? a : b` en Java), écrit dans l'autre ordre. Une liste non vide vaut vrai : s'il y a des erreurs, on rend `None`.

**Le piège classique : « réparer » le texte en silence.** Le cas le plus fréquent d'un JSON illisible est un modèle qui entoure sa réponse d'un bloc de code Markdown : trois accents graves, le mot `json`, un saut de ligne, puis l'objet. On est tenté de retirer ces lignes avant `json.loads`. La solution ne le fait pas : elle signale l'erreur, et la boucle de réparation la renvoie au modèle, qui apprend dans la conversation à répondre en JSON pur. Nettoyer en silence masquerait une dérive du prompt ou du modèle, qu'on ne verrait plus dans les mesures (étape 11 du cours). Si l'on choisit un jour de nettoyer, on le fait explicitement, et l'on compte combien de fois c'était nécessaire.

**Un autre piège : `NaN`.** `json.loads` accepte par défaut `NaN` et `Infinity`, qui ne sont pas du JSON. La lecture réussit donc, mais `validate` refuse ensuite la valeur grâce au test `math.isfinite` de l'étape 2.

**Vérifier à la main.** Le texte commence par un accent grave. Au caractère 0, `json.loads` attend une valeur JSON (une accolade, un crochet, un guillemet, un chiffre, `true`, `false` ou `null`) et trouve un accent grave : l'erreur est `Expecting value` à la position 0.

```text
# [extrait] console
>>> from agent.schemas import SCHEMA_DEMANDE_CREDIT, lire_et_valider
>>> lire_et_valider('{"montant_aed": 1,}', SCHEMA_DEMANDE_CREDIT)
(None, ['$ : JSON illisible (Illegal trailing comma before end of object, position 17)'])
>>> lire_et_valider('{"montant_aed": 0}', SCHEMA_DEMANDE_CREDIT)[1][-1]
'$.montant_aed : 0 doit être > 0'
```

La virgule finale, permise en JavaScript, est interdite en JSON ; le message de Python dit exactement laquelle.

## Le test qui passe maintenant

```powershell
python -m unittest -v tests.test_02_schemas.TestReparation.test_json_dans_un_bloc_de_code
```

Le test fabrique le texte d'un bloc de code Markdown qui entoure `{}` et vérifie que la fonction rend `(None, ["$ : JSON illisible (Expecting value, position 0)"])`.

## Ce qu'il faut retenir

- Le modèle rend du texte : on lit, puis on valide, et l'échec de lecture devient une erreur de validation à la racine.
- On n'attrape que l'exception attendue, `json.JSONDecodeError`, jamais `Exception`.
- Les données ne sortent que si elles sont valides : sinon, `None`.

> Suivant : [Étape 6 — La boucle de réparation](<06-Boucle-de-reparation.md>)
