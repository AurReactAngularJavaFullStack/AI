# 07-Contexte — Formule 08 — KV Cache (principe)

**Dossier :** 07-Contexte  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, AI Platform Team  

**Nom du fichier :** 07-Contexte-Formule-08-KV-Cache.md

## Définition complète

Pendant l’inférence, les Keys et Values des tokens précédents ne changent pas. On les met en cache pour éviter de les recalculer.

À l’étape $t$ :

$$
K_{\text{cache}} = [K_1, K_2, \ldots, K_{t-1}, K_t]
$$

$$
V_{\text{cache}} = [V_1, V_2, \ldots, V_{t-1}, V_t]
$$

On ne calcule que $Q_t$, $K_t$, $V_t$ pour le nouveau token, puis on concatène avec le cache.

### Définition de chaque symbole

- $K_{\text{cache}}$, $V_{\text{cache}}$ : représentations mises en cache.
- $t$ : étape de génération courante.
- Complexité par token : passe de $O(n^2)$ à $O(n)$ grâce au cache.

### Comportement

Accélère fortement la génération, surtout pour les longues séquences. Utilisé dans tous les LLM modernes en production.

## Code Python (conceptuel)

```python
# cache_k = concat(cache_k, new_k)
# cache_v = concat(cache_v, new_v)
# attention avec Q_new et les caches
```

## Cas d’usage métier

Indispensable pour des agents réactifs en production (chatbots métier, analyse de documents longs, génération de rapports).
