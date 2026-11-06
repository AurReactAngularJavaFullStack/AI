# 11-Evaluation — Formule 01 — Faithfulness

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 11-Evaluation-Formule-01-Faithfulness.md

## Définition complète

$$
\text{Faithfulness} = \frac{|V|}{|S|}
$$



- \(S\) : ensemble des claims extraits de la réponse.
- \(V\) : claims supportées par le contexte.
- Plus |V| est grand relativement à |S|, plus le score est élevé (moins d’hallucinations).

## Code Python

```python
def faithfulness(claims, is_supported):
    if not claims: return float('nan')
    return sum(is_supported(c) for c in claims) / len(claims)
```

## Cas d’usage métier maximum

**Finance / Banque** : Vérifier qu’une recommandation d’investissement ou un rapport de conformité ne contient aucune affirmation inventée par rapport aux documents réglementaires récupérés. Seuil strict (> 0.95) obligatoire.

**Immobilier** : Une estimation de prix ou une description de bien ne doit pas inventer des caractéristiques (DPE, surface) absentes des documents sources.

**Crypto** : Une analyse de protocole ne doit pas inventer des mécanismes de tokenomics non présents dans le whitepaper.

**Bancaire / Crédit** : La justification d’un refus ou d’un accord de crédit doit être strictement fondée sur les règles et le dossier récupérés.

**Assurance, RH, BTP** : Même logique pour éviter toute hallucination sur des montants, des délais ou des obligations légales.

Un score bas bloque systématiquement la réponse automatique dans ces domaines à fort enjeu.
