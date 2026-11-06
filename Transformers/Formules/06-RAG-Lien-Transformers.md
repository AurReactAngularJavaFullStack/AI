# 06-RAG — Lien avec les Transformers

**Dossier :** 06-RAG  
**Métiers :** AI Engineers, AI Agent Ops

## Rappel

Le RAG combine un retriever (souvent basé sur des embeddings Transformer) et un générateur (LLM Transformer).

Les embeddings utilisés pour la similarité cosinus proviennent généralement d’un modèle Transformer (encoder).

## Pipeline typique

1. Embedding de la requête et des documents
2. Retrieval (cosine, hybrid…)
3. Construction du prompt avec le contexte
4. Génération par le LLM

## Cas d’usage

Tous les cas déjà détaillés dans les fichiers 06-RAG (finance, immobilier, etc.).
