# LangChain — Memory

**Dossier :** 05-Memoire / LangChain  

## Types de mémoire

- ConversationBufferMemory : historique complet
- ConversationBufferWindowMemory : dernières k messages
- ConversationSummaryMemory : résumé
- VectorStoreRetrieverMemory : mémoire via retrieval

## Exemple

```python
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
```

## Cas d’usage

Conversations multi-tours dans les agents RH, assurance, support client.
