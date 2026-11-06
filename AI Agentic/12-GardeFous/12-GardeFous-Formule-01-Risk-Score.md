# 12-GardeFous — Formule 01 — Score de risque

**Dossier :** 12-GardeFous  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Agent Ops, AI Engineers, Forward-Deployed Engineers, AI Platform Team  

**Nom du fichier :** 12-GardeFous-Formule-01-Risk-Score.md

## Définition

Un score de risque agrège plusieurs signaux pour décider si une action d’agent doit être bloquée, revue ou autorisée.

$$
\text{risque} = w_1 \cdot \text{sensibilité\_données} + w_2 \cdot \text{impact\_action} + w_3 \cdot \text{incertitude\_modèle}
$$

### Définition de chaque symbole

- \(\text{sensibilité_données}\) : niveau de sensibilité des données manipulées (0-1).
- \(\text{impact_action}\) : gravité potentielle de l’action (écriture, paiement, décision irréversible).
- \(\text{incertitude_modèle}\) : signal de faible confiance (perplexité haute, Faithfulness basse, etc.).
- \(w_i\) : poids. Un seuil sur le score final déclenche un garde-fou (blocage ou human-in-the-loop).

### Comportement

- Plus un des composants augmente, plus le risque global augmente.
- Au-dessus d’un seuil (ex. 0.7), l’action est bloquée ou escaladée.

## Code Python

```python
def risk_score(sensibilite: float, impact: float, incertitude: float,
               w1: float = 0.4, w2: float = 0.4, w3: float = 0.2) -> float:
    return w1 * sensibilite + w2 * impact + w3 * incertitude
```

## Cas d’usage métier maximum

**Finance / Banque** : bloquer une recommandation si le risque dépasse le seuil.

**Crypto** : exiger une confirmation humaine pour toute transaction au-dessus d’un certain risque.

**Immobilier / Assurance / RH** : protéger les actions sensibles et les données personnelles.

**Secteur public** : respect strict des habilitations.

Ce score est le cœur de nombreux systèmes de guardrails en production.
