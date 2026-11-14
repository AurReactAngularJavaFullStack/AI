"""Palier 02 — schémas et validation : refuser des arguments mal formés avant tout effet.

Origine : étape 77, section 3 (validateur minimal : mêmes chemins JSON, mêmes messages, onze mots-clés),
et étape 8 (boucle de réparation, probabilité de succès après relances).

Trois pièces :
- `validate` rend la liste des écarts entre une instance et un schéma, avec leurs chemins JSON ;
- `schema_pour_api_strict` prépare le schéma envoyé à l'API en mode strict, qui refuse les bornes ;
- `reparer` renvoie les erreurs au modèle et lui redemande un JSON, au plus `max_essais` fois.
"""
import json
import math
import re

MOTS_CLES = {"type", "properties", "required", "additionalProperties", "minimum", "maximum", "exclusiveMinimum",
             "minLength", "maxLength", "pattern", "description"}
TYPES = {"object": (dict,), "string": (str,), "number": (int, float), "integer": (int,)}
NOMS_JSON = {bool: "boolean", int: "integer", float: "number", str: "string", list: "array", dict: "object"}


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Liste des écarts (vide si l'instance est conforme). Un mot-clé inconnu lève `ValueError`.

    Le contrôle de type exclut d'abord les booléens : en Python, `isinstance(True, int)` est vrai.
    Un type faux arrête la validation de ce nœud (comparer "300" à un maximum n'aurait pas de sens).
    Exemple : `validate({"n_mois": "300"}, {"type": "object", "properties": {"n_mois": {"type": "integer"}}})`
    vaut ["$.n_mois : type attendu integer, reçu string"] ; `validate(0, {"exclusiveMinimum": 0})`
    vaut ["$ : 0 doit être > 0"].
    """
    inconnus = set(schema) - MOTS_CLES
    if inconnus:
        raise ValueError(f"mots-clés non pris en charge : {sorted(inconnus)}")   # refuser plutôt qu'ignorer
    attendu = schema.get("type")
    if attendu and (isinstance(instance, bool) or not isinstance(instance, TYPES[attendu])):   # True n'est pas 1
        return [f"{path} : type attendu {attendu}, reçu {NOMS_JSON.get(type(instance), 'null')}"]
    erreurs = []
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if not math.isfinite(instance):
            return [f"{path} : nombre non fini ({instance}), interdit en JSON"]
        if "minimum" in schema and instance < schema["minimum"]:
            erreurs.append(f"{path} : {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            erreurs.append(f"{path} : {instance} > maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            erreurs.append(f"{path} : {instance} doit être > {schema['exclusiveMinimum']}")
    elif isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            erreurs.append(f"{path} : longueur {len(instance)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            erreurs.append(f"{path} : {instance!r} ne respecte pas le motif {schema['pattern']}")
    elif isinstance(instance, dict):
        proprietes = schema.get("properties", {})
        erreurs += [f"{path} : champ obligatoire absent « {c} »" for c in schema.get("required", []) if c not in instance]
        for cle, valeur in instance.items():
            if cle in proprietes:
                erreurs += validate(valeur, proprietes[cle], f"{path}.{cle}")
            elif schema.get("additionalProperties", True) is False:
                erreurs.append(f"{path} : champ non prévu « {cle} »")
    return erreurs


def objet(proprietes: dict) -> dict:
    """Schéma d'objet strict : tous les champs obligatoires, aucun champ non prévu.

    Exemple : `objet({"x": {"type": "number"}})` vaut {"type": "object", "properties": {"x": {"type":
    "number"}}, "required": ["x"], "additionalProperties": False}.
    """
    return {"type": "object", "properties": proprietes, "required": list(proprietes), "additionalProperties": False}


NON_STRICT = ("minimum", "maximum", "exclusiveMinimum", "minLength", "maxLength")


def schema_pour_api_strict(schema: dict) -> dict:
    """Le mode strict de l'API refuse les bornes : on les retire et on les recopie dans la description.

    La validation locale (`validate`) reste la seule à vérifier ces bornes.
    Exemple : {"type": "integer", "minimum": 1, "maximum": 300} devient
    {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."}.
    """
    copie = {k: v for k, v in schema.items() if k not in NON_STRICT and k != "properties"}
    if "properties" in schema:
        copie["properties"] = {nom: schema_pour_api_strict(sous) for nom, sous in schema["properties"].items()}
    retirees = [f"{k}={v}" for k, v in schema.items() if k in NON_STRICT]
    if retirees:
        copie["description"] = (schema.get("description", "") + " Contraintes : " + ", ".join(retirees) + ".").strip()
    return copie


MOTIF_EMIRATES_ID = "^784-[0-9]{4}-[0-9]{7}-[0-9]$"
SCHEMA_DEMANDE_CREDIT = {                      # écrit en toutes lettres : c'est ce que rendrait objet({...})
    "type": "object",
    "properties": {
        "montant_aed": {"type": "number", "exclusiveMinimum": 0},
        "duree_mois": {"type": "integer", "minimum": 12, "maximum": 300},
        "revenu_mensuel_aed": {"type": "number", "exclusiveMinimum": 0},
        "emirates_id": {"type": "string", "pattern": MOTIF_EMIRATES_ID},
    },
    "required": ["montant_aed", "duree_mois", "revenu_mensuel_aed", "emirates_id"],
    "additionalProperties": False,
}


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


def reparer(llm, schema: dict, demande: str, max_essais: int = 3) -> dict:
    """Boucle de réparation : appel → `lire_et_valider` → erreurs renvoyées au modèle → nouvel essai.

    Rend {"statut", "donnees", "essais", "erreurs"} ; `statut` vaut "valide", "echec" (après
    `max_essais` essais ratés : l'appelant passe la main à un humain), "refusal" ou "max_tokens"
    (traités AVANT de lire le contenu : un refus ne se répare pas). `erreurs` a une liste par essai lu.
    Exemple : un premier JSON où "duree_mois" vaut "36", puis un JSON correct : statut "valide",
    essais 2, erreurs [["$.duree_mois : type attendu integer, reçu string"], []].
    """
    if max_essais < 1:
        raise ValueError("max_essais doit valoir au moins 1")
    system = "Réponds uniquement par un objet JSON conforme à ce schéma : " + json.dumps(schema, ensure_ascii=False)
    messages = [{"role": "user", "content": demande}]
    erreurs_par_essai = []
    for essai in range(1, max_essais + 1):
        reponse = llm.create(system=system, messages=messages, tools=[])
        if reponse.stop_reason in ("refusal", "max_tokens"):
            return {"statut": reponse.stop_reason, "donnees": None, "essais": essai, "erreurs": erreurs_par_essai}
        brut = "".join(b.text for b in reponse.content if b.type == "text")
        donnees, erreurs = lire_et_valider(brut, schema)
        erreurs_par_essai.append(erreurs)
        if not erreurs:
            return {"statut": "valide", "donnees": donnees, "essais": essai, "erreurs": erreurs_par_essai}
        messages.append({"role": "assistant", "content": reponse.content})
        messages.append({"role": "user", "content": "Ta réponse ne respecte pas le schéma :\n" + "\n".join(erreurs)
                         + "\nRenvoie uniquement l'objet JSON corrigé."})
    return {"statut": "echec", "donnees": None, "essais": max_essais, "erreurs": erreurs_par_essai}


def p_succes(p: float, relances: int) -> float:
    """P = 1 − (1 − p)^(R + 1) : au moins un essai valide parmi R + 1 essais indépendants (étape 8).

    `reparer(..., max_essais=R + 1)` fait au plus R relances. Exemple : `p_succes(0.9, 2)` = 0.999.
    """
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")
    return 1 - (1 - p) ** (relances + 1)


def essais_moyens(p: float, relances: int) -> float:
    """E[A] = 1 + (1 − p) + … + (1 − p)^R : l'essai i + 1 n'a lieu que si les i premiers ont échoué.

    Exemple : `essais_moyens(0.9, 2)` = 1 + 0.1 + 0.01 = 1.11 appels au modèle en moyenne.
    """
    if not 0 < p <= 1 or relances < 0:
        raise ValueError("il faut 0 < p <= 1 et relances >= 0")
    return sum((1 - p) ** i for i in range(relances + 1))
