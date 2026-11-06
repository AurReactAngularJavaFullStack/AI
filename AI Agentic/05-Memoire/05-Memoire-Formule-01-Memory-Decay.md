# 05-Memoire — Formule 01 — Décroissance temporelle (Memory Decay)

**Dossier :** 05-Memoire  
**Chapitre / Section :** 02-Formules-Theoremes-Algorithmes  
**Métiers concernés :** AI Engineers, AI Agent Ops  

**Nom du fichier :** 05-Memoire-Formule-01-Memory-Decay.md

## Définition complète

Une fonction de décroissance permet de réduire progressivement l’importance des souvenirs anciens.

$$
\text{score}(t) = \text{score}_0 \cdot e^{-\lambda t}
$$
ou version linéaire :

$$
\text{score}(t) = \text{score}_0 \cdot \max(0, 1 - \alpha t)
$$


### Définition de chaque symbole

- \(\text{score}_0\) : importance initiale du souvenir.
- \(t\) : temps écoulé (ou nombre d’interactions).
- \(\lambda\) ou \(\alpha\) : taux de décroissance. Plus il est grand, plus le souvenir s’efface vite.
- \(e^{-\lambda t}\) : décroissance exponentielle (douce au début, plus rapide ensuite).

### Comportement

- Plus \(\lambda\) augmente, plus les souvenirs anciens deviennent négligeables rapidement.
- Utile pour éviter que la mémoire soit saturée par des informations obsolètes.

## Code Python

```python
import math

def exponential_decay(score0: float, t: float, lambda_: float = 0.1) -> float:
    return score0 * math.exp(-lambda_ * t)
```

## Cas d’usage métier maximum

**Finance / Banque** : réduire l’importance d’anciennes préférences de risque si le profil client a changé.

**Immobilier** : oublier progressivement des critères de recherche anciens.

**Crypto** : diminuer le poids d’alertes ou de positions anciennes.

**RH / Assurance** : mémoire de dossier qui s’estompe si non réactivée.

Cette formule aide à maintenir une mémoire pertinente et à jour.
