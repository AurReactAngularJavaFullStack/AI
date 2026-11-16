## 3. **Théorème de Continuité (pour les LLMs)**

*Établit la stabilité des prédictions des LLMs par rapport à leurs entrées.*

- **Énoncé formel (Théorème 1)** : 

  Soit E l'espace des embeddings (ex: RrR*r*) et P l'espace des vecteurs de probabilité multinomiaux. 

  Si une transformation T:E→P préserve la convexité (une combinaison linéaire d'embeddings est mappée sur la même combinaison linéaire des probabilités correspondantes) et est bornée, alors T est continue.

- **Définition** : 

  Ce théorème assure qu'une petite modification dans l'espace d'embedding d'un prompt (représentation vectorielle du texte) provoque seulement un petit changement dans la distribution de probabilité prédite pour le token suivant.

- **Démonstration (esquisse)** : 

  La preuve repose sur les propriétés des opérateurs linéaires (ou affine) bornés entre espaces vectoriels normés. La préservation de la convexité et la bornitude impliquent la continuité selon les principes de l'analyse fonctionnelle.

- **Exemple** : 

  Les prompts "Le chat est sur le tapis" et "Le chat se trouve sur le tapis" ont des embeddings similaires. Le théorème garantit que les distributions de probabilité pour le mot suivant générées par le LLM seront également très proches.

- **Rôle dans les LLMs** : 

  La continuité est **cruciale pour la généralisation**. 

  Elle permet au modèle de produire des prédictions raisonnables et stables pour des prompts qu'il n'a jamais vus exactement pendant l'entraînement, évitant des sauts brusques et incohérents dans la génération de texte.