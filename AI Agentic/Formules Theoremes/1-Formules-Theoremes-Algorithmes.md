# 11-Evaluation — 02-Formules, Théorèmes et Algorithmes

**Leçon longue et détaillée — Métriques mathématiques avec démonstrations complètes et code Python**

## Introduction narrative étendue

Dans un projet comme StaffMind, un agent qui qualifie une demande d’onboarding RH peut sembler correct lors d’un test manuel. Mais après quelques semaines en production, des utilisateurs signalent que certaines réponses inventent des délais de déclaration ou omettent des conditions fiscales. Sans métriques quantitatives, il est difficile de savoir si le problème vient du prompt, du retrieval ou du modèle. Les formules de Faithfulness, Answer Relevancy, Precision, Recall et F1 permettent de transformer ces retours qualitatifs en scores mesurables, de poser des seuils dans une pipeline CI/CD (comme tu le faisais avec GitLab CI à la Banque de France), et de bloquer un déploiement qui ferait chuter la qualité.

Nous allons détailler chaque formule avec plusieurs exemples numériques complets, des démonstrations pas à pas, et le code Python correspondant.

## 1. Faithfulness

### Définition

On extrait un ensemble de claims (affirmations atomiques) \( S \) de la réponse générée. Un juge (souvent un LLM) détermine le sous-ensemble \( V \subseteq S \) de claims supportées par le contexte récupéré.

$$
\text{Faithfulness} = \frac{|V|}{|S|}
$$
Si \( |S| = 0 \), le score est indéfini.

### Démonstration détaillée — Exemple 1 (assurance)

**Contexte récupéré** :  

« Pour un choc sur parking, le plafond de garantie dommages matériels est de 1 500 €. La franchise standard est de 150 €. Aucune franchise ne s’applique si le véhicule est stationné et que le conducteur n’est pas présent. »

**Réponse générée** :  

« Le plafond de garantie pour un choc sur parking est de 1 500 € et la franchise est de 300 €. Aucune franchise ne s’applique. »

**Claims extraits** :
1. « Le plafond de garantie pour un choc sur parking est de 1 500 € » → supporté (\( V \))
2. « la franchise est de 300 € » → non supporté (hallucination)
3. « Aucune franchise ne s’applique » → partiellement supporté, mais on le considère non strictement déductible sans condition → non supporté pour cet exemple strict

\( |S| = 3 \), \( |V| = 1 \)  
$$
\text{Faithfulness} = \frac{1}{3} \approx 0.333
$$


### Démonstration détaillée — Exemple 2 (RH StaffMind)

**Contexte** : « Au Royaume-Uni, un salarié en période d’essai peut prendre des congés payés après 3 mois de service effectif, sous réserve d’accord de l’employeur. »

**Réponse** : « Au Royaume-Uni, un salarié en période d’essai peut prendre des congés payés immédiatement. »

Claims :
1. « Au Royaume-Uni, un salarié en période d’essai peut prendre des congés payés » → supporté
2. « immédiatement » → non supporté

Faithfulness = 1/2 = 0.5

### Code Python correspondant

```python
from typing import List, Callable

def faithfulness(claims: List[str], is_supported: Callable[[str], bool]) -> float:
    """
    Calcule le score de Faithfulness.
    is_supported : fonction qui retourne True si le claim est supporté par le contexte.
    """
    if not claims:
        return float('nan')
    supported = sum(1 for claim in claims if is_supported(claim))
    return supported / len(claims)

# Exemple d'utilisation
claims = [
    "Le plafond est de 1500 €",
    "la franchise est de 300 €",
    "Aucune franchise ne s'applique"
]
def mock_judge(claim: str) -> bool:
    return "1500" in claim  # simulation simple

print(faithfulness(claims, mock_judge))  # 0.333...
```

## 2. Answer Relevancy

### Définition

On génère \( n \) questions hypothétiques à partir de la réponse, on calcule leur embedding, puis la similarité cosinus moyenne avec l’embedding de la question originale.

$$
\text{Answer Relevancy} = \frac{1}{n} \sum_{i=1}^{n} \cos(E_{g_i}, E_o) = \frac{1}{n} \sum_{i=1}^{n} \frac{E_{g_i} \cdot E_o}{\|E_{g_i}\| \|E_o\|}
$$


### Démonstration numérique complète

Supposons des embeddings simplifiés à 2 dimensions pour la démonstration :

Question originale \( E_o = [0.9, 0.1] \)

Questions générées :
- \( E_{g1} = [0.85, 0.15] \)
- \( E_{g2} = [0.7, 0.4] \)
- \( E_{g3} = [0.2, 0.8] \)

Calculs des cosinus (formule détaillée) :

Pour \( g1 \) :
$$
\cos = \frac{0.9\times0.85 + 0.1\times0.15}{\sqrt{0.9^2+0.1^2} \sqrt{0.85^2+0.15^2}} = \frac{0.765 + 0.015}{\sqrt{0.82} \sqrt{0.745}} \approx \frac{0.78}{0.9055 \times 0.8631} \approx \frac{0.78}{0.781} \approx 0.999
$$
Pour \( g2 \) : ≈ 0.89  
Pour \( g3 \) : ≈ 0.34  

Moyenne : \( (0.999 + 0.89 + 0.34)/3 \approx 0.743 \)

### Code Python

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def answer_relevancy(original_embedding: np.ndarray, generated_embeddings: List[np.ndarray]) -> float:
    if not generated_embeddings:
        return 0.0
    sims = [cosine_similarity(original_embedding, g) for g in generated_embeddings]
    return float(np.mean(sims))

# Exemple
eo = np.array([0.9, 0.1])
generated = [np.array([0.85, 0.15]), np.array([0.7, 0.4]), np.array([0.2, 0.8])]
print(answer_relevancy(eo, generated))
```

## 3. Precision, Recall et F1

$$
\text{Precision} = \frac{TP}{TP + FP}, \quad
\text{Recall} = \frac{TP}{TP + FN}, \quad
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$



### Exemple complet (appels d’outils)

Appels attendus : `get_policy(country="UK")`, `check_eligibility()`  
Appels réels : `get_policy(country="UK")`, `get_policy(country="FR")`, `check_eligibility()`

- TP = 2 (`get_policy UK` et `check_eligibility`)
- FP = 1 (`get_policy FR`)
- FN = 0

Precision = 2/3 ≈ 0.667  
Recall = 2/2 = 1.0  
F1 ≈ 0.8

### Code Python

```python
def precision_recall_f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

print(precision_recall_f1(2, 1, 0))
```

## 4. Autres métriques (Context Precision, ToolCall F1)

Les formules suivent le même esprit. Le code Python pour ToolCall F1 utilise des ensembles pour comparer les appels indépendamment de l’ordre.

## Cas d’usage réels supplémentaires

Dans VerifactureBTP, on peut mesurer la Faithfulness d’une facture générée par rapport aux règles légales récupérées. Un score < 0.95 bloque la génération automatique.

Dans un contexte Banque de France, on combine Faithfulness avec une métrique de non-divulgation d’informations sensibles.

## À retenir

Chaque formule est accompagnée de démonstrations chiffrées complètes et de code Python prêt à être adapté. Ces outils permettent de passer d’une évaluation subjective à une évaluation reproductible et intégrable dans une chaîne de livraison continue.
