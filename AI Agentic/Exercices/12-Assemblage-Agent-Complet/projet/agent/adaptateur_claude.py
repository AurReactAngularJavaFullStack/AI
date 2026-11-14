"""Palier 12 — l'adaptateur Claude : le même port que `FakeLLM`, branché sur l'API. Jamais exécuté par les tests.

Origine : étape 77, section « Passer au vrai LLM » (adaptateur de l'étape 13).
Prérequis : `pip install anthropic`, puis une clé `ANTHROPIC_API_KEY` ou un profil créé par `ant auth login`.
L'import d'`anthropic` est DANS le constructeur : importer ce module ne demande ni le SDK ni le réseau,
et le reste du paquet reste en bibliothèque standard.

Usage, une seule ligne change :
    agent = Agent(ClaudeLLM())            # au lieu de construire_agent(script)
    resultat = agent.repondre(question)

Les outils sont déjà au bon format : `Registre.definitions_api()` retire les bornes refusées par le
mode strict et les recopie dans les descriptions, pendant que la porte locale continue de les vérifier.
Quatre règles de l'API, déjà respectées par `executer_agent` : pas de `tool_choice` forcé ; tous les
`tool_result` d'une étape dans un seul message `user` ; `reponse.content` recopié tel quel (blocs de
réflexion compris) ; `stop_reason == "refusal"` traité avant de lire le contenu.
"""


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
