# 11-Evaluation — Formule 01 — Faithfulness

**Dossier :** 11-Evaluation  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops, Forward-Deployed Engineers, Product Engineers  

**Nom du fichier :** 11-Evaluation-Formule-01-Faithfulness.md

## Définition complète de chaque élément

La Faithfulness mesure la proportion des affirmations (claims) de la réponse générée qui sont réellement supportées par le contexte récupéré. C’est la métrique anti-hallucination principale.

$$
\text{Faithfulness} = \frac{|V|}{|S|}
$$


### Définition de chaque symbole

- \(S\) : l’ensemble de toutes les claims atomiques extraites de la réponse générée. Chaque claim est une phrase courte et autonome (« Le plafond est de 1 500 € »).
- \(V\) : le sous-ensemble de \(S\) dont les claims sont jugées supportées (déductibles) du contexte récupéré par un juge (humain ou LLM).
- \(|V|\) : le nombre de claims supportées.
- \(|S|\) : le nombre total de claims. Si \(|S| = 0\), le score est indéfini.
- Le ratio est compris entre 0 et 1. 1 = aucune hallucination, 0 = tout est inventé.

### Comportement quand les valeurs changent

- Plus \(|V|\) augmente (plus de claims supportées), plus le score augmente → réponse plus fiable.
- Plus \(|S|\) augmente sans que \(|V|\) augmente (claims supplémentaires non supportées), plus le score baisse → plus d’hallucinations.
- Un score qui passe de 0.95 à 0.70 après un changement de prompt signifie que le modèle invente davantage ; on bloque généralement le déploiement.

## Démonstration complète avec interprétation

**Contexte :** « Plafond dommages parking = 1 500 €. Franchise standard = 150 €. »

**Réponse :** « Le plafond est de 1 500 € et la franchise est de 300 €. Aucune franchise ne s’applique. »

Claims :
1. « Le plafond est de 1 500 € » → supporté → dans \(V\)
2. « la franchise est de 300 € » → non supporté
3. « Aucune franchise ne s’applique » → non supporté

\(|S| = 3\), \(|V| = 1\)  
$$
\text{Faithfulness} = \frac{1}{3} \approx 0.333
$$
**Interprétation :**  
Le score de 0.333 indique une réponse peu fiable. Sur trois affirmations, deux sont inventées. Dans un contexte d’assurance ou de RH, on ne laisserait pas l’agent répondre automatiquement. On corrigerait le prompt ou on ajouterait un garde-fou.

## Code Python

```python
from typing import List, Callable

def faithfulness(claims: List[str], is_supported: Callable[[str], bool]) -> float:
    """
    |V| / |S|
    Plus le résultat est proche de 1, moins il y a d'hallucinations.
    """
    if not claims:
        return float('nan')
    supported_count = sum(1 for c in claims if is_supported(c))
    return supported_count / len(claims)

# Exemple
claims = [
    "Le plafond est de 1500 €",
    "la franchise est de 300 €",
    "Aucune franchise ne s'applique"
]
def judge(claim: str) -> bool:
    return "1500" in claim

score = faithfulness(claims, judge)
print(f"Faithfulness = {score:.3f}")
print("Interprétation : score bas → beaucoup d'hallucinations, ne pas déployer")
```

## Cas d’usage

Dans VerifactureBTP ou StaffMind, un seuil de Faithfulness ≥ 0.90 est souvent exigé avant de laisser un agent générer une facture ou une réponse de conformité.
