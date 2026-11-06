# LangChain — Prompts et Prompt Templates

**Dossier :** 01-Prompts / LangChain  

## Types de prompts

- PromptTemplate : template simple avec variables
- ChatPromptTemplate : pour les modèles de chat (system, human, AI)
- FewShotPromptTemplate : avec exemples

## Exemple

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple words."
)
```

## Bonnes pratiques

- Être clair et spécifique
- Utiliser des few-shot quand nécessaire
- Séparer la logique du prompt du code

## Cas d’usage

Tous les agents métier (conformité, estimation, onboarding…).
