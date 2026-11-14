"""Palier 04 — le registre d'outils : un nom, un contrat, une porte de validation par outil.

Origine : étape 77, section 8 (`Outil`, décorateur `outil`, `porte`, `definitions_api`, outils EAU),
sans la partie garde-fous (politique, risque, approbation), qui arrive au palier 09 par composition.

Le registre est un objet, pas une variable globale : chaque agent (et chaque test) a le sien.
`Registre.porte(nom)` fabrique l'appelable que verra la boucle : il valide les arguments contre le
schéma, lève `ArgumentsInvalides` en cas d'écart, et seulement ensuite exécute la fonction métier.
`executer_appel` exécute un bloc `tool_use` et rend toujours un `tool_result` : une erreur est
renvoyée au modèle avec `is_error`, jamais avalée.
"""
import json
from collections.abc import Callable
from dataclasses import dataclass

from agent.metier import AED_PAR_USD, gratuite_fin_de_service, mensualite, ratio_endettement, tva
from agent.schemas import objet, schema_pour_api_strict, validate


@dataclass
class Outil:
    """Un outil enregistré : son nom public, sa description pour le modèle, son schéma, sa fonction."""
    nom: str
    description: str
    schema: dict
    fonction: Callable


class RefusPolitique(PermissionError):
    """La politique a dit non : l'outil n'est pas atteint (levée par les garde-fous, palier 09)."""


class ArgumentsInvalides(ValueError):
    """Le schéma a dit non : l'outil n'est pas atteint."""


class ErreurOutil(Exception):
    """L'outil lui-même refuse (outil inconnu, garde-fou interne, refus humain)."""


class Registre:
    """Table nom → `Outil`. Exemple : après `enregistrer_outils_metier(Registre())`, `len(registre)` vaut 5."""

    def __init__(self) -> None:
        self.outils: dict[str, Outil] = {}

    def __len__(self) -> int:
        return len(self.outils)

    def __contains__(self, nom: str) -> bool:
        return nom in self.outils

    def outil(self, nom: str, description: str, schema: dict):
        """Décorateur : enregistre la fonction sous son nom public, avec son contrat.

        Un nom vide ou déjà pris lève `ValueError` ; la fonction décorée est rendue inchangée.
        Exemple : `@registre.outil("tva", "TVA de 5 %", objet({...}))` au-dessus de `def outil_tva(...)`.
        """
        if not nom:
            raise ValueError("un outil a un nom non vide")
        if nom in self.outils:
            raise ValueError(f"outil déjà enregistré : {nom}")

        def enregistrer(fonction: Callable) -> Callable:
            self.outils[nom] = Outil(nom, description, schema, fonction)
            return fonction
        return enregistrer

    def porte(self, nom: str) -> Callable:
        """L'appelable que voit la boucle : schéma d'abord, fonction ensuite.

        Exemple : `porte("mensualite")(principal=1_000_000, taux_annuel=0.045, n_mois="300")` lève
        `ArgumentsInvalides("$.n_mois : type attendu integer, reçu string")` sans exécuter le calcul.
        """
        if nom not in self.outils:
            raise ValueError(f"outil inconnu : {nom}")
        o = self.outils[nom]

        def appeler(**arguments):
            erreurs = validate(arguments, o.schema)
            if erreurs:
                raise ArgumentsInvalides(" ; ".join(erreurs))
            return o.fonction(**arguments)
        return appeler

    def appelables(self) -> dict[str, Callable]:
        """Le dictionnaire nom → porte que l'on passe à la boucle d'agent."""
        return {nom: self.porte(nom) for nom in self.outils}

    def definitions_api(self) -> list[dict]:
        """Les définitions au format de l'API, en mode strict : bornes retirées, recopiées en description.

        Exemple : pour "mensualite", `input_schema["properties"]["n_mois"]` vaut
        {"type": "integer", "description": "Contraintes : minimum=1, maximum=300."} et `strict` vaut True.
        """
        return [{"name": o.nom, "description": o.description, "input_schema": schema_pour_api_strict(o.schema),
                 "strict": True} for o in self.outils.values()]


def executer_appel(outils: dict, bloc) -> tuple[dict, tuple]:
    """Exécute un bloc `tool_use` ; rend (tool_result, ligne de trace). Aucune exception ne sort.

    Succès : `content` est la sortie en JSON, la trace vaut (nom, arguments, sortie).
    Échec : `content` vaut « NomDeLException: message », `is_error` vaut True, et la trace porte
    « ERREUR message ». Un outil inconnu donne « ErreurOutil: outil inconnu : x ».
    Exemple : un appel à "tva" avec {"montant_ht": 100} donne le contenu '{"tva_aed": 5.0, "ttc_aed": 105.0}'.
    """
    try:
        if bloc.name not in outils:
            raise ErreurOutil(f"outil inconnu : {bloc.name}")
        sortie = outils[bloc.name](**bloc.input)
        return ({"type": "tool_result", "tool_use_id": bloc.id, "content": json.dumps(sortie, ensure_ascii=False)},
                (bloc.name, bloc.input, sortie))
    except Exception as e:                    # l'erreur repart vers le modèle, elle n'est pas avalée
        return ({"type": "tool_result", "tool_use_id": bloc.id, "content": f"{type(e).__name__}: {e}",
                 "is_error": True}, (bloc.name, bloc.input, f"ERREUR {e}"))


def enregistrer_outils_metier(registre: Registre) -> Registre:
    """Enregistre les cinq outils de calcul EAU de l'étape 77 (schémas complets) ; rend le registre.

    Sorties arrondies comme dans 77 : mensualité au centime, ratio à 4 décimales, USD au centime.
    Exemple : "ratio_endettement" avec existantes=6 000, nouvelle=5 558.32, revenu=40 000 rend
    {"ratio": 0.289, "recevable": True} ; "convertir_aed_usd" avec 5 558.32 rend {"montant_usd": 1513.5}.
    """
    @registre.outil("mensualite", "Mensualité d'un prêt amortissable, en AED.", objet({
        "principal": {"type": "number", "exclusiveMinimum": 0},
        "taux_annuel": {"type": "number", "minimum": 0, "maximum": 0.3},
        "n_mois": {"type": "integer", "minimum": 1, "maximum": 300}}))
    def outil_mensualite(principal: float, taux_annuel: float, n_mois: int) -> dict:
        return {"mensualite_aed": round(mensualite(principal, taux_annuel, n_mois), 2)}

    @registre.outil("ratio_endettement",
                    "Endettement total CBUAE : (mensualités existantes + nouvelle) / revenu, plafond 50 %.",
                    objet({"existantes": {"type": "number", "minimum": 0},
                           "nouvelle": {"type": "number", "exclusiveMinimum": 0},
                           "revenu": {"type": "number", "exclusiveMinimum": 0}}))
    def outil_ratio(existantes: float, nouvelle: float, revenu: float) -> dict:
        ratio, recevable = ratio_endettement(existantes, nouvelle, revenu)
        return {"ratio": round(ratio, 4), "recevable": recevable}

    @registre.outil("convertir_aed_usd",
                    "Convertit un montant en AED vers l'USD, à la parité fixe de 3,6725 AED pour 1 USD.",
                    objet({"montant_aed": {"type": "number", "minimum": 0}}))
    def outil_conversion(montant_aed: float) -> dict:
        return {"montant_usd": round(montant_aed / AED_PAR_USD, 2)}

    @registre.outil("gratuite_fin_de_service",
                    "Indemnité de fin de service (décret-loi fédéral 33/2021, secteur privé), en AED.",
                    objet({"salaire_base_mensuel": {"type": "number", "exclusiveMinimum": 0},
                           "annees": {"type": "number", "minimum": 0, "maximum": 60}}))
    def outil_gratuite(salaire_base_mensuel: float, annees: float) -> dict:
        return {"indemnite_aed": round(gratuite_fin_de_service(salaire_base_mensuel, annees), 2)}

    @registre.outil("tva", "TVA de 5 % et montant TTC, en AED.", objet({"montant_ht": {"type": "number", "minimum": 0}}))
    def outil_tva(montant_ht: float) -> dict:
        return {"tva_aed": round(tva(montant_ht), 2), "ttc_aed": round(montant_ht + tva(montant_ht), 2)}

    return registre
