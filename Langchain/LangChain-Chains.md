# LangChain — Chains

**Dossier :** 04-Agents / LangChain  

## Qu’est-ce qu’une Chain ?

Une séquence de composants exécutés dans un ordre logique (LLM + prompt + output parser, etc.).

## Types courants

- LLMChain
- SequentialChain
- RetrievalQA Chain (pour le RAG)
- ConversationalChain

## Exemple simple

```python
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
response = chain.invoke({"topic": "LangChain"})
```

## Cas d’usage

Workflows structurés multi-étapes dans les agents métier.
