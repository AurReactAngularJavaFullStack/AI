# 07-Contexte — 02-Formules et Mécanisme d’Attention

**Leçon longue — Scaled Dot-Product Attention pour AI Software Engineer**

## Introduction narrative

Même si tu n’entraînes pas de modèles from scratch, comprendre le mécanisme d’attention t’aide à diagnostiquer les problèmes de contexte long. Quand un agent StaffMind doit gérer une conversation de 40 messages sur un onboarding complexe (documents, validations multi-pays, exceptions), le modèle « oublie » parfois une information importante située au milieu de l’historique. La formule d’attention explique pourquoi et comment les techniques de context engineering (compaction, summarization, selective retrieval) tentent de compenser cette limitation.

## Formule du Scaled Dot-Product Attention

La formule fondamentale introduite dans le papier « Attention is All You Need » est :

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V
$$
où :
- $$
  Q \in \mathbb{R}^{n_q \times d_k}
  $$

  : matrice des queries

- $$
  K \in \mathbb{R}^{n_k \times d_k}
  $$

   : matrice des keys

- $$
  V \in \mathbb{R}^{n_k \times d_v}
  $$

   : matrice des values

- \(d_k\) : dimension des vecteurs query/key

- $$
  \sqrt{d_k}
  $$

   : facteur de scaling

### Pourquoi le scaling par \(\sqrt{d_k}\) ?

Si les composantes de \(Q\) et \(K\) sont des variables aléatoires de moyenne 0 et variance 1, le produit scalaire a une variance égale à \(d_k\). Sans division par \(
$$
\sqrt{d_k}\
$$
), les scores deviennent très grands quand \(d_k\) augmente (64, 128…), le softmax sature (valeurs proches de 0 ou 1), et les gradients disparaissent. Le scaling maintient la variance des scores proche de 1.

### Lettres grecques et notations

- \(d_k\) : dimension (parfois notée 
  $$
  d_{\text{model}} / h
  $$
   pour multi-head)

- Softmax appliqué ligne par ligne

- Parfois on note
  $$
  \alpha_{ij}
  $$
  \) les poids d’attention normalisés

## Algorithme détaillé (une seule query pour simplifier)

1. Calculer les scores bruts : 
   $$
   s_j = \mathbf{q} \cdot \mathbf{k}_j
   $$
    pour chaque key \(j\).

2. Scaler :
   $$
   s_j' = s_j / \sqrt{d_k}
   $$
   .

3. Appliquer softmax :  
   $$
   p_j = \frac{\exp(s_j')}{\sum_l \exp(s_l')}
   $$
   
   
4. Calculer la sortie : 
   $$
   \mathbf{o} = \sum_j p_j \mathbf{v}_j
   $$
   .

En matrices, tout se fait en une multiplication.

## Cas d’usage réel : conversation longue d’onboarding RH

Un nouvel employé au Royaume-Uni envoie successivement :
- ses documents d’identité,
- une question sur la pension,
- une exception liée à un double statut fiscal,
- puis demande un récapitulatif.

Sans gestion de contexte, l’information sur le double statut (message 12) peut être « diluée » par l’attention. Les techniques pratiques (summarization des anciens messages, retrieval sélectif des passages critiques, ou fenêtres glissantes) sont des contournements de la limitation imposée par la formule d’attention et la taille de la fenêtre de contexte.

## À retenir

La formule d’attention explique le comportement des LLM face à de longs contextes. Connaître le rôle de \(\sqrt{d_k}\) et du softmax te permet de mieux interpréter pourquoi certaines informations sont « oubliées » et quelles stratégies d’ingénierie de contexte (compaction, RAG hybride, mémoire externe) sont les plus efficaces pour tes agents métier.
