# Étape 7 — Assemblage et vérification

> Palier 08 · Étape 7 sur 7 · Précédent : [Étape 6 — Calendrier et chemin critique](<06-Calendrier-et-chemin-critique.md>) · Suivant : [Palier 09 — Garde-fous](<../../../09-Garde-Fous/README.md>) · Retour à l'énoncé : [README du palier 08](<../../README.md>)

## Comment raisonner

Le module est complet. On le relit dans l'ordre des dépendances entre fonctions, on lance toute la suite de tests (les paliers précédents doivent rester verts : ce palier n'importe rien d'eux, mais une faute de manipulation dans `agent/` est vite arrivée), puis la démo, qui rejoue le dossier du client C-6.

## Le plan du module

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`Tache.__post_init__()`** — C'est la méthode de l'étape 1, le contrôleur qui tamponne chaque fiche de travail avant qu'elle ne soit scellée : appelée par le constructeur de la dataclass gelée, elle lève `ValueError` pour un nom vide ou une durée négative, puis range les prérequis en tuple sans doublon, dans leur ordre de première apparition. Elle ne renvoie rien ; c'est grâce à elle que le décompte de Kahn reste juste et que les 8 tâches du dossier de crédit peuvent être créées.

**`_graphe(taches)`** — C'est la fonction privée de l'étape 2, le géomètre qui relève le plan : elle reçoit les tâches, les indexe par nom, refuse une tâche en double ou un prérequis inconnu par `ValueError`, retourne chaque arc pour obtenir les successeurs et compte les degrés entrants. Elle renvoie ce triplet de dictionnaires à `tri_topologique`, seul à l'appeler ; sur le dossier de crédit, les degrés entrants totalisent 8, le nombre d'arcs du plan.

**`_nommer_cycle(restants, par_nom)`** — C'est la fonction privée de l'étape 4, l'enquêteur qui remonte les dépendances des tâches bloquées : elle reçoit l'ensemble des tâches que Kahn n'a pas sorties et l'index par nom, remonte du plus petit nom vers le plus petit prérequis restant jusqu'à revoir une tâche, puis renvoie le cycle dans le sens des arcs, commencé et terminé par son plus petit nom. Au point 6 de la démo, elle nomme la boucle de quatre tâches qui va de `evaluer_risque` à `verifier_identite` en passant par `relancer_client`.

**`tri_topologique(taches)`** — C'est le chef de chantier de l'étape 3 : il reçoit les tâches, les fait valider par `_graphe`, sort à chaque tour le plus petit nom du tas des tâches prêtes et libère ses successeurs, puis lève `ValueError` avec le cycle nommé s'il reste des tâches, ou renvoie l'ordre complet. C'est le point unique de validation du module ; au point 1 de la démo, il rend l'ordre qui commence par `lire_memoire` et finit par `rediger_reponse`.

**`vagues(taches)`** — C'est le régisseur de l'étape 5 : il reçoit les tâches, obtient l'ordre topologique, donne à chaque tâche le niveau 1 + le plus haut niveau de ses prérequis, 0 sans prérequis, et renvoie la liste des vagues, chacune triée par nom. Au point 2 de la démo, il rend cinq vagues, trois tâches indépendantes au départ puis une chaîne jusqu'à `rediger_reponse`.

**`calendrier(taches)`** — C'est l'agenda de l'étape 6, pour un atelier aux exécutants illimités : il reçoit les tâches, parcourt l'ordre topologique et donne à chacune un début égal à la plus grande fin de ses prérequis et une fin égale à ce début plus sa durée. Il renvoie le dictionnaire nom → (début, fin) ; au point 3 de la démo, `evaluer_risque` occupe le créneau de 2,0 s à 3,2 s et `rediger_reponse` celui de 3,2 s à 5,7 s.

**`chemin_critique(taches)`** — C'est l'enquêteur de l'étape 6, qui désigne la chaîne qui fixe la durée du dossier : il reçoit les tâches, part de celle qui finit le plus tard et remonte vers le prérequis qui finit le plus tard, puis renvoie la durée et le chemin dans l'ordre d'exécution, `(0.0, [])` pour un plan vide. Au point 4 de la démo, il rend 5,7 s par `rechercher_regles`, `evaluer_risque` et `rediger_reponse`, et au point 5, la recherche accélérée à 0,8 s, 5,6 s par la branche du calcul.

**`duree_par_vagues(taches)`** — C'est le chronomètre de l'étape 6, pour un atelier qui attend la fin de chaque vague avant de lancer la suivante : il reçoit les tâches et renvoie la somme, sur les vagues, de la plus grande durée de chaque vague. Au point 4 de la démo, il donne 7,1 s, entre les 9,5 s du séquentiel et les 5,7 s du chemin critique ; le gain de 40 % affiché sur la même ligne est celui du chemin critique sur le séquentiel, et non celui des vagues.

**`dossier_credit()`** — C'est le classeur de référence de l'étape 1 : elle ne reçoit rien et renvoie une liste neuve des 8 tâches du dossier de crédit, avec leurs durées illustratives en secondes et leurs prérequis. Toute la démo du client C-6 en part, y compris le plan circulaire du point 6, obtenu en faisant attendre à `verifier_identite` une nouvelle tâche `relancer_client`, qui attend elle-même `rediger_reponse`.

```python
# [extrait] agent/planification.py
import heapq
from dataclasses import dataclass
...
@dataclass(frozen=True)
class Tache:
    ...
    def __post_init__(self) -> None:
        ...
def _graphe(taches: list[Tache]) -> tuple[dict, dict, dict]:
    ...
def _nommer_cycle(restants: set[str], par_nom: dict) -> list[str]:
    ...
def tri_topologique(taches: list[Tache]) -> list[str]:
    ...
def vagues(taches: list[Tache]) -> list[list[str]]:
    ...
def calendrier(taches: list[Tache]) -> dict[str, tuple[float, float]]:
    ...
def chemin_critique(taches: list[Tache]) -> tuple[float, list[str]]:
    ...
def duree_par_vagues(taches: list[Tache]) -> float:
    ...
def dossier_credit() -> list[Tache]:
    ...
```

Qui appelle qui :

```text
tri_topologique ──► _graphe            (contrôles, successeurs, degrés entrants)
       │        └─► _nommer_cycle      (seulement si Kahn s'arrête trop tôt)
       ├──◄ vagues ──◄ duree_par_vagues
       └──◄ calendrier ──◄ chemin_critique
Tache ◄── utilisée partout ; dossier_credit ── les données d'exemple
```

Toute la validation passe par un seul point, `tri_topologique` : `vagues`, `calendrier` et donc `chemin_critique` refusent un plan circulaire avec le même message, sans une ligne de code en plus. C'est le même principe qu'au palier 04, où toute la validation des arguments passait par la porte.

## Tous les tests

Depuis `projet/` :

```powershell
python -m unittest -v
```

Tous les tests des paliers 01 à 08 doivent être verts, dont les 12 du palier 08 : 2 dans `TestTache`, 4 dans `TestTriTopologique`, 2 dans `TestVagues` et 4 dans `TestCheminCritique`.

## La démo

```powershell
python demo.py
```

Sortie attendue, identique à celle de l'énoncé :

```text
Palier 08 — dossier de crédit du client C-6 à l'agence A-3 (durées illustratives, en secondes)
1. Ordre de Kahn (départage alphabétique) : lire_memoire → calculer_mensualite → calculer_ratio → convertir_usd → rechercher_regles → verifier_identite → evaluer_risque → rediger_reponse
2. Vagues parallèles :
   vague 1 : lire_memoire, rechercher_regles, verifier_identite
   vague 2 : calculer_mensualite
   vague 3 : calculer_ratio, convertir_usd
   vague 4 : evaluer_risque
   vague 5 : rediger_reponse
3. Calendrier au plus tôt, exécutants illimités :
   evaluer_risque   de 2.0 s à 3.2 s
   rediger_reponse  de 3.2 s à 5.7 s
4. Chemin critique : rechercher_regles → evaluer_risque → rediger_reponse = 5.7 s
   séquentiel 9.5 s ; vagues synchronisées 7.1 s ; gain du parallélisme 40.0%
5. Recherche accélérée à 0.8 s : 5.6 s, le chemin critique devient lire_memoire → calculer_mensualite → calculer_ratio → evaluer_risque → rediger_reponse
6. Plan circulaire refusé : cycle détecté : evaluer_risque → rediger_reponse → relancer_client → verifier_identite → evaluer_risque
OK — palier 08 terminé.
```

Ce que tu dois savoir expliquer, ligne par ligne :

- **1.** L'ordre de Kahn, avec le tas : `lire_memoire` d'abord (« l » avant « r » et « v »), puis toute la branche du calcul, qui devient prête au fur et à mesure (étape 3).
- **2.** Cinq vagues : trois tâches indépendantes au départ, puis une chaîne (étape 5).
- **3.** `evaluer_risque` attend le plus tardif de ses trois prérequis, la recherche, finie à 2,0 s (étape 6).
- **4.** 5,7 s par le chemin critique, contre 7,1 s par vagues et 9,5 s en séquentiel : 1 − 5,7 / 9,5 = 40 % de gain (étape 6).
- **5.** Accélérer la recherche ne fait gagner que 0,1 s : la branche du calcul devient critique (étape 6).
- **6.** Un plan où l'on relance le client avant de vérifier son identité est circulaire : le message nomme les quatre tâches de la boucle (étape 4).

## Ce que tu as appris

- Modéliser une tâche comme un objet valeur immuable, qui se valide à la construction, et se méfier des valeurs par défaut mutables.
- Retourner les arcs d'un graphe (prérequis → successeurs) et compter les degrés entrants, en refusant les doublons et les références inconnues.
- Coder Kahn avec un tas pour obtenir un ordre unique, et transformer un échec de Kahn en un cycle nommé, lisible par un humain ou par le modèle qui doit corriger son plan.
- Calculer en un passage sur l'ordre topologique les niveaux (les vagues) et les dates au plus tôt : de la programmation dynamique, dans l'esprit de Bellman.
- Distinguer trois durées, 9,5 s, 7,1 s et 5,7 s, et savoir que seules les tâches du chemin critique valent la peine d'être optimisées.

## Et ensuite

L'agent sait chercher, planifier et calculer. Mais certaines de ses actions sont irréversibles : un virement de 180 000 AED ne s'annule pas. Au [palier 09 — Garde-fous](<../../../09-Garde-Fous/README.md>), tu lui ajoutes une politique d'accès par rôle, le masquage des données personnelles dans un journal d'audit chaîné, un score de risque, un veto sur l'irréversible et une approbation humaine qui, sans réponse, vaut refus.
