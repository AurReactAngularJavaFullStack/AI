## 12. **Théorème de la Dimension VC (Vapnik-Chervonenkis)**

*Fondement de la théorie de l'apprentissage statistique.*

- **Énoncé formel** : Soit HH une classe d'hypothèses de fonctions h:X→{0,1}*h*:X→{0,1}. La dimension VC de HH, notée VCdim(H)*V**C**d**im*(H), est le plus grand entier d tel qu'il existe un ensemble de d points que HH peut "shatter" (séparer selon toutes les 2d2*d* labellisations possibles).

- **Définition** : La dimension VC mesure la capacité d'une classe de modèles à représenter des fonctions complexes. Des bornes de généralisation en dépendent directement.

- **Démonstration des bornes (esquisse)** : La théorie VC établit que avec probabilité au moins 1−δ1−*δ*, pour tout h∈H*h*∈H :

  R(h)≤Rn(h)+ Rootsquare(()(VCdim(H)*log⁡(n/VCdim(H))+log⁡(1/δ))/n

  où R(h) est le risque réel et Rn(h) le risque empirique.

- **Exemple** : 

  Pour les classifieurs linéaires en dimension d, VCdim=d+1.

- **Rôle dans les LLMs / Arbres** :

  - **Contrôle de capacité** : 

    Pour les arbres de décision, la dimension VC est liée à la profondeur et au nombre de feuilles. Cela justifie les techniques d'élagage (pruning).

  - **Analyse théorique** : 

    Bien que difficile à calculer exactement pour les réseaux de neurones modernes, la théorie VC fournit le cadre conceptuel pour comprendre le compromis biais-variance et l'importance de la régularisation.