# LangChain — RAG (Retrieval Augmented Generation)

**Dossier :** 06-RAG / LangChain  

## Pipeline RAG avec LangChain

1. Document Loaders
2. Text Splitters
3. Embeddings
4. Vector Store
5. Retriever
6. Chain (RetrievalQA ou LCEL)

## Vector Stores populaires

FAISS, Chroma, Pinecone, Weaviate, Qdrant…

## Exemple simplifié

```python
from langchain.chains import RetrievalQA
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

## Cas d’usage

Tous les cas RAG déjà détaillés (finance, immobilier, crypto…).
