# 01-Prompts — Formule 01 — Score de conformité du prompt

**Dossier :** 01-Prompts  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** Product Engineers, AI Engineers, Forward-Deployed Engineers  

**Nom du fichier :** 01-Prompts-Formule-01-Prompt-Compliance-Score.md

## Définition complète

Un score simple pour évaluer si un system prompt respecte les bonnes pratiques métier.

$$
\text{score} = w_1 \cdot \text{rôle clair} + w_2 \cdot \text{contraintes} + w_3 \cdot \text{format sortie} + w_4 \cdot \text{sources obligatoires} - w_5 \cdot \text{risque injection}
$$


### Définition de chaque symbole

- Chaque composant est un score entre 0 et 1 (présence et qualité).
- \(w_i\) : poids. Plus le poids d’un critère critique (sources, contraintes) est élevé, plus il influence le score final.
- Un score bas indique un prompt fragile pour la production.

### Comportement

- Plus les éléments de sécurité et de clarté sont présents, plus le score augmente.
- Un risque d’injection élevé fait baisser le score.

## Code Python

```python
def prompt_compliance_score(role: float, constraints: float, output_format: float,
                            sources: float, injection_risk: float) -> float:
    return 0.2*role + 0.25*constraints + 0.2*output_format + 0.25*sources - 0.1*injection_risk
```

## Cas d’usage métier

**Finance, Banque, Immobilier, Crypto, Assurance** : vérifier avant déploiement qu’un prompt impose bien la citation des sources et interdit les inventions.
