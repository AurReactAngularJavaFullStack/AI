# LangChain — Agents et Tools

**Dossier :** 04-Agents / LangChain  

## Agents

Un agent utilise un LLM pour décider quelles actions (tools) appeler, dans quel ordre, et quand s’arrêter.

## Pattern ReAct

Thought → Action → Observation → répéter.

## Tools

Fonctions que l’agent peut appeler (search, calculatrice, API métier, base de données…).

## Exemple

```python
from langchain.agents import initialize_agent, Tool
tools = [Tool(name="Search", func=search, description="...")]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

## Cas d’usage métier

Agents qui appellent des outils de scoring, de conformité, de recherche de comparables, etc.
