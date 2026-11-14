# 8. Files d'Attente — Formules Manquantes

## Leçon 8.1 : Formules M/M/1 (File d'attente Markovienne)

**Définition**  
Modèle de file d'attente avec arrivées Poisson (λ) et service exponentiel (μ), un seul serveur.

**Rôle**  
Dimensionner précisément un agent backend unique (ex. : un microservice d'inférence LLM).

### Équations Mathématiques

$$
\rho = \frac{\lambda}{\mu} \quad \text{(Facteur d'utilisation, doit être < 1)}
$$

$$
P_0 = 1 - \rho \quad \text{(Probabilité que le serveur soit vide)}
$$

$$
L = \frac{\rho}{1 - \rho} \quad \text{(Nombre moyen de requêtes dans le système)}
$$

$$
L_q = \frac{\rho^2}{1 - \rho} \quad \text{(Nombre moyen en attente)}
$$

$$
W = \frac{1}{\mu - \lambda} \quad \text{(Temps moyen dans le système)}
$$

$$
W_q = \frac{\rho}{\mu - \lambda} \quad \text{(Temps moyen d'attente)}
$$

### Code Python

```python
def mm1_queue(lambda_rate, mu_rate):
    """Calcule les métriques d'une file M/M/1"""
    if lambda_rate >= mu_rate:
        raise ValueError("Système instable : λ doit être < μ")
    
    rho = lambda_rate / mu_rate
    P0 = 1 - rho
    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu_rate - lambda_rate)
    Wq = rho / (mu_rate - lambda_rate)
    
    return {
        "ρ (utilisation)": rho,
        "P₀ (serveur vide)": P0,
        "L (req. dans système)": L,
        "Lq (req. en attente)": Lq,
        "W (temps système)": W,
        "Wq (temps attente)": Wq
    }

metrics = mm1_queue(lambda_rate=6, mu_rate=8)
for k, v in metrics.items():
    print(f"{k}: {v:.3f}")
```

### Démonstration Quantifiée

Avec λ = 6, μ = 8 :
- ρ = 0.75 (75 % d'utilisation)
- L = 3 requêtes en moyenne dans le système
- W = 0.5 seconde en moyenne
- Effet de levier : Si λ passe à 7.5, W explose à 2 secondes !

---

## Leçon 8.2 : Formule d'Erlang C (Multi-serveurs M/M/c)

**Définition**  
Probabilité qu'une requête arrivante doive attendre (tous les c serveurs occupés) dans un système à c serveurs identiques.

**Rôle**  
Dimensionner le nombre d'instances d'un agent pour respecter un SLA.

### Équation Mathématique

$$
P_W = C(c, \lambda/\mu) = \frac{\frac{(\lambda/\mu)^c}{c!} \cdot \frac{c}{c - \lambda/\mu}}{\sum_{k=0}^{c-1} \frac{(\lambda/\mu)^k}{k!} + \frac{(\lambda/\mu)^c}{c!} \cdot \frac{c}{c - \lambda/\mu}}
$$

$$
W_q = \frac{P_W}{c\mu - \lambda}
$$

### Code Python

```python
from math import factorial

def erlang_c(c, lambda_rate, mu_rate):
    """Probabilité d'attente dans un système M/M/c"""
    rho = lambda_rate / (c * mu_rate)
    if rho >= 1:
        return 1.0
    
    a = lambda_rate / mu_rate
    
    sum_terms = sum((a**k) / factorial(k) for k in range(c))
    last_term = ((a**c) / factorial(c)) * (c / (c - a))
    
    P_W = last_term / (sum_terms + last_term)
    W_q = P_W / (c * mu_rate - lambda_rate)
    L_q = lambda_rate * W_q
    
    return {"P_W": P_W, "W_q": W_q, "L_q": L_q}

result = erlang_c(c=3, lambda_rate=10, mu_rate=4)
print(f"Probabilité d'attente : {result['P_W']:.3f}")
print(f"Temps d'attente moyen : {result['W_q']:.3f}s")
```

---

## Leçon 8.3 : Notation de Kendall

**Définition**  
Notation standardisée A/S/c/K/N/D pour décrire une file d'attente :

- A : Distribution des arrivées (M = Markovienne/Poisson, D = Déterministe, G = Générale)
- S : Distribution du service
- c : Nombre de serveurs
- K : Capacité du système (optionnel, ∞ par défaut)
- N : Taille de la population (optionnel)
- D : Discipline de service (FIFO, LIFO, Priority)

**Rôle**  
Communiquer précisément l'architecture d'un système agentique entre ingénieurs.

### Exemples

- **M/M/1** : Agent unique, arrivées Poisson, service exponentiel
- **M/M/c/K** : c agents, file limitée à K requêtes (rate limiting)
- **M/G/1** : Agent unique, service de distribution générale (ex. : LLM avec temps variable)

---

## Synthèse des Formules Manquantes

| Fichier              | Formules Présentes              | Formules Manquantes (Ajoutées)                       |
| -------------------- | ------------------------------- | ---------------------------------------------------- |
| 04 - Graphes         | Matrice d'adjacence, Acyclicité | Tri topologique, Détection de cycle DFS              |
| 05 - Evaluation      | Précision, Rappel, F1, D_KL     | Spécificité, Perplexité, AUC-ROC                     |
| 06 - Transformer     | Scaled Dot-Product              | Multi-Head Attention, Positional Encoding, LayerNorm |
| 07 - Optimisation    | Gradient Descent, LoRA          | Adam, Backpropagation, L1/L2 Regularization          |
| 08 - Files d'attente | Loi de Little                   | M/M/1, Erlang C, Notation de Kendall                 |

Toutes les formules sont formatées pour Typora (blocs `$$...$$`, lettres grecques correctement transcrites) avec code Python fonctionnel et démonstrations quantifiées.

## Lecture

Le déroulé avec les nombres est dans `08a_MM1_Queue.md`, `08b_Erlang_C.md` et `08c_Kendall_Notation.md`.

Pour un agent, λ = 3, μ = 4 : ρ = 0,75, trois requêtes en moyenne dans le système, une seconde de séjour, dont 0,75 s d'attente et 0,25 s de service. Le dénominateur μ − λ est la marge avec laquelle on rattrape une rafale. Elle passe de 1 à 0,2 si λ monte à 3,8, et le séjour passe de 1 s à 5 s sans que le modèle soit devenu plus lent.

Pour quatre instances, λ = 12, μ = 4 : Erlang C vaut environ 0,51. Une question sur deux trouve les quatre agents occupés. L'attente moyenne ne vaut pas celle d'un M/M/1 : on ne fait attendre que cette moitié-là, d'où

$$
W_q \approx 0{,}13
$$

s.
