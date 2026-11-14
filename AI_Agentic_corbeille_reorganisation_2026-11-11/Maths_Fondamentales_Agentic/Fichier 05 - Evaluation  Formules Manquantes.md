## Fichier 05 - Evaluation : Formules Manquantes

### Leçon 5.1 : Matrice de Confusion Complète et Spécificité

**Définition** Extension des métriques de base avec la **Spécificité** (capacité à correctly identifier les négatifs) et la **Précision Négative** (Negative Predictive Value).

**Rôle** Essentiel pour les cas où les faux positifs ET les faux négatifs ont des coûts asymétriques (ex: diagnostic médical).

**Équations Mathématiques**

Speˊcificiteˊ=TNTN+FPSpeˊcificiteˊ=*T**N*+*F**P**T**N*

NPV (Negative Predictive Value)=TNTN+FNNPV (Negative Predictive Value)=*T**N*+*F**N**T**N*

Exactitude (Accuracy)=TP+TNTP+TN+FP+FNExactitude (Accuracy)=*T**P*+*T**N*+*F**P*+*F**N**T**P*+*T**N*

**Code Python**

```python
def confusion_matrix_metrics(tp, tn, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "Précision": precision, "Rappel": recall,
        "Spécificité": specificity, "NPV": npv,
        "Exactitude": accuracy, "F1": f1
    }

# Exemple : Agent de détection de fraude
# 100 transactions : 10 fraudes, 90 légitimes
# Agent détecte : 8 fraudes (TP), 2 manquées (FN), 5 fausses alertes (FP), 85 correctes (TN)
print(confusion_matrix_metrics(tp=8, tn=85, fp=5, fn=2))
```

**Démonstration Quantifiée** Avec TP=8,TN=85,FP=5,FN=2*T**P*=8,*T**N*=85,*F**P*=5,*F**N*=2 :

- Spécificité = 85/(85+5)=0.94485/(85+5)=0.944 → L'agent identifie bien les transactions légitimes
- NPV = 85/(85+2)=0.97785/(85+2)=0.977 → Quand il dit "pas de fraude", il a raison à 97.7%

### Leçon 5.2 : Perplexité (Évaluation des LLM)

**Définition** La perplexité mesure à quel point un modèle de langage est "surpris" par un texte. C'est la métrique reine pour évaluer la qualité prédictive d'un LLM.

**Rôle** Évaluer si un LLM fine-tuné (ex: avec LoRA) a bien appris le domaine cible sans dégrader ses capacités générales.

**Équation Mathématique**

$$
\mathrm{Perplexity}(W) = \sqrt[N]{\prod_{i=1}^{N} \frac{1}{P(w_i \mid w_{1:i-1})}} = \exp\left( -\frac{1}{N} \sum_{i=1}^{N} \log P(w_i \mid w_{1:i-1}) \right)
$$

Où W=w1,w2,…,wN est une séquence de N tokens.

**Code Python**

```python
import numpy as np

def compute_perplexity(log_probs):
    """
    log_probs: liste des log-probabilités de chaque token
    """
    N = len(log_probs)
    avg_neg_log_prob = -np.mean(log_probs)
    perplexity = np.exp(avg_neg_log_prob)
    return perplexity

# Exemple : Un LLM prédit 5 tokens avec log-probs [-0.1, -0.5, -2.3, -0.2, -0.4]
log_probs = [-0.1, -0.5, -2.3, -0.2, -0.4]
print(f"Perplexity: {compute_perplexity(log_probs):.2f}")
# Sortie : ~3.19 (faible perplexité = modèle confiant)
```

**Démonstration Quantifiée**

- Si P(wi)=0.5 pour tous les tokens (modèle très confiant) : PPL=2P
- Si P(wi)=0.01 (modèle très surpris) : PPL=100
- **Interprétation** : Une perplexité de 10 signifie qu'en moyenne, le modèle hésite entre 10 mots à chaque position.

**Cas d'usage réels** Comparaison d'un LLM généraliste vs un LLM spécialisé (ex: Llama 3 vs Llama 3 + LoRA juridique). Si la perplexité sur un corpus juridique baisse de 45 à 15, le fine-tuning est réussi.

### Leçon 5.3 : AUC-ROC (Courbe ROC et Aire Sous la Courbe)

**Définition** L'AUC (Area Under Curve) mesure la capacité d'un modèle à discriminer entre classes positives et négatives à travers tous les seuils de décision possibles.

**Rôle** Évaluer un agent de classification (ex: détection de spam, modération de contenu) indépendamment du seuil choisi.

**Équation Mathématique**

$$
\mathrm{AUC} = \int_{0}^{1} \mathrm{TPR}\bigl(\mathrm{FPR}^{-1}(t)\bigr)\, dt
$$

$$
\mathrm{TPR} = \frac{TP}{TP + FN} \quad (\text{Rappel}), \qquad
\mathrm{FPR} = \frac{FP}{FP + TN}
$$

**Code Python**

```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# Scores de confiance d'un agent de modération
y_true = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0]  # 1 = contenu toxique
y_scores = [0.9, 0.8, 0.3, 0.95, 0.2, 0.85, 0.1, 0.4, 0.75, 0.35]

auc = roc_auc_score(y_true, y_scores)
print(f"AUC: {auc:.3f}")

# Tracé de la courbe ROC
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
plt.plot(fpr, tpr, label=f'ROC (AUC = {auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--')  # Ligne de hasard
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
```

**Démonstration Quantifiée**

- AUC = 0.5 : Modèle aléatoire (aussi bon qu'un lancer de pièce)
- AUC = 0.7-0.8 : Acceptable
- AUC = 0.9-1.0 : Excellent
- AUC = 1.0 : Classification parfaite

**Cas d'usage réels** Évaluation d'un agent de détection de deepfakes. Un AUC de 0.93 signifie que si on prend un deepfake et une vraie vidéo au hasard, l'agent a 93% de chances de donner un score plus élevé au deepfake.

## Lecture

Les fractions du début de ce fichier sont écrites deux fois, en texte brut, et ne s'affichent pas comme des formules. Le calcul est raconté dans `05a_Specificite_NPV_AUC.md` et `05b_Perplexite_LLM.md`.

Sur 1000 paiements dont 10 fraudes, avec `TP = 5`, `FP = 3`, `FN = 5`, `TN = 987` : la spécificité vaut 0,997, l'accuracy vaut 0,992, et un agent qui ne marque jamais rien aurait déjà 0,990. L'accuracy félicite celui qui ne fait rien. L'AUC, elle, ne choisit pas de seuil : sur les scores 0,4 et 0,9 pour les fraudes, 0,1 et 0,6 pour les honnêtes, trois paires sur quatre mettent la fraude au-dessus, donc l'AUC vaut 0,75.

La perplexité n'est pas une accuracy. Sur les probabilités 0,5, 0,5 et 0,2 données aux trois tokens réellement écrits, elle vaut la racine cubique de 20, environ 2,71. C'est le nombre de candidats entre lesquels l'agent semblait hésiter à chaque mot.