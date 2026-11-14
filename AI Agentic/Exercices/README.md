# Exercices : construire un agent IA pas à pas

> Dossier d'exercices, à part du parcours · Parcours complet : [00 — Parcours de lecture](<../00-Parcours-de-Lecture.md>) · Agent de référence : [Étape 77 — Projet final](<../13-Projet-Final/77-Projet-Final-Agent-From-Scratch.md>) · Révision : [14 — Synthèse et révision](<../14-Synthese-et-Revision/78-Synthese-Mathematiques-de-l-Agent-IA.md>)

Ce dossier te fait coder, en douze paliers, l'agent complet de l'étape 77. Chaque palier ajoute une pièce, dans l'ordre du cours : on commence par parler au modèle, on finit par un agent qui cherche dans des documents, appelle des outils métier des Émirats, se protège, se mesure et tient en production. À la fin, tu as écrit toi-même chaque ligne de l'agent, et tu sais le refaire depuis une feuille blanche.

Tout tourne avec la bibliothèque standard de Python, sans clé d'API : le modèle de langage est un faux modèle scripté (`FakeLLM`), qui répond toujours la même chose dans le même ordre. Les tests sont donc reproductibles. Le palier 12 montre comment brancher le vrai modèle, Claude, à la place du faux, sans changer le reste du code.

## Comment est organisé un palier

```text
NN-Nom-du-palier/
  README.md              l'énoncé : rappel de cours, spécification chiffrée, cas d'usage, sortie attendue
  projet/                là où tu travailles
    agent/               les modules des paliers précédents (déjà faits) + le squelette du palier
    tests/               les tests unittest de tous les paliers jusqu'à celui-ci
    demo.py              un petit scénario qui utilise ce que tu viens de coder
  solutions/             la solution entière du palier
    agent/  tests/  demo.py
    progression/         la solution construite pas à pas : chaque bloc de code est suivi
                         d'explications détaillées (pourquoi, comment, pièges, test qui passe)
```

Le squelette du palier contient les signatures, les docstrings (la spécification de chaque fonction, avec un exemple chiffré) et des `# TODO`. Chaque corps lève `NotImplementedError` : c'est à toi de l'écrire. Les modules des paliers précédents sont fournis complets, pour que chaque palier soit indépendant : tu peux commencer n'importe où, même si le plus utile est de suivre l'ordre.

## Comment travailler

1. Lire le `README.md` du palier en entier, rappel de cours compris. Refaire sur une feuille A4 les exemples chiffrés de la spécification.
2. Ouvrir `projet/agent/<module>.py` et coder les fonctions dans l'ordre de la section « Travail à faire » du README.
3. Lancer les tests après chaque fonction. Au départ, les tests du palier échouent tous par `NotImplementedError` ; les tests des paliers précédents, eux, passent déjà.
4. Quand tous les tests sont verts, lancer `demo.py` et comparer sa sortie à « Sortie attendue de demo.py » dans le README.
5. Si tu bloques, ouvrir `solutions/progression/` : la solution y est construite étape par étape, et tu peux t'arrêter dès que tu as compris l'idée qui te manquait. En dernier recours seulement, comparer avec `solutions/agent/`.
6. Le lendemain, effacer ton module et le récrire sans regarder. Le palier est acquis quand tu le refais seul, tests verts du premier coup.

## Lancer les tests

Dans PowerShell, depuis le dossier `projet/` du palier (ou `solutions/` pour voir la solution passer) :

```text
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m unittest -v
& "C:\Users\aur95\AppData\Local\Python\pythoncore-3.14-64\python.exe" demo.py
```

Pour un seul test, par exemple au palier 05 : `python -m unittest -v tests.test_05_boucle`. Le code reste compatible avec Python 3.10 et suivants.

## Les douze paliers

| Palier | Ce que tu codes | Module | Étapes du cours |
| --- | --- | --- | --- |
| [01 — Modèle et prompt](<01-Modele-et-Prompt/README.md>) | le faux modèle scripté, les messages, le prompt système qui isole les documents non fiables | `agent/modele.py` | 1 à 7 |
| [02 — Schémas et validation](<02-Schemas-et-Validation/README.md>) | un validateur de schéma JSON écrit à la main et une boucle de réparation | `agent/schemas.py` | 8 à 11 |
| [03 — Outils métier EAU](<03-Outils-Metier-EAU/README.md>) | mensualité, taux d'endettement CBUAE, fin de service, TVA, IBAN AE, Emirates ID | `agent/metier.py` | 8 à 12 |
| [04 — Registre d'outils](<04-Registre-d-Outils/README.md>) | le registre, la porte qui valide les arguments, l'enveloppe d'erreur | `agent/outils.py` | 12, 46 à 49 |
| [05 — Boucle d'agent](<05-Boucle-d-Agent/README.md>) | la boucle ReAct et ses trois arrêts | `agent/boucle.py` | 1, 13 |
| [06 — Mémoire](<06-Memoire/README.md>) | similarité, décroissance temporelle, score de pertinence, rappel des souvenirs | `agent/memoire.py` | 14 à 17 |
| [07 — Recherche hybride](<07-Recherche-Hybride/README.md>) | BM25, plongements, cosinus, fusion RRF, citations | `agent/recherche.py` | 18 à 30 |
| [08 — Planification DAG](<08-Planification-DAG/README.md>) | découper une demande en tâches, tri topologique, vagues parallèles, chemin critique | `agent/planification.py` | 38 à 45 |
| [09 — Garde-fous](<09-Garde-Fous/README.md>) | politique d'accès, masquage, score de risque, veto, approbation humaine, journal d'audit chaîné | `agent/garde_fous.py` | 66, 67 |
| [10 — Évaluation](<10-Evaluation/README.md>) | Tool Call F1, Goal Accuracy, intervalle de Wilson, fidélité, barrière d'intégration continue | `agent/evaluation.py` | 50 à 65 |
| [11 — Production et coûts](<11-Production-et-Couts/README.md>) | coût d'une tâche, seau à jetons, relances avec attente exponentielle, p95, budget | `agent/production.py` | 68 à 72 |
| [12 — Assemblage](<12-Assemblage-Agent-Complet/README.md>) | l'agent complet, et l'adaptateur qui branche Claude à la place du faux modèle | `agent/assemblage.py` | 77 |

## Ce que tu sais faire à la fin

- Écrire la boucle d'un agent qui raisonne, appelle des outils et s'arrête toujours, quel que soit le modèle.
- Valider tout ce que le modèle propose avant de l'exécuter, et renvoyer au modèle une erreur qu'il peut corriger.
- Coder des outils métier exacts pour les Émirats (crédit, fin de service, TVA, identifiants), testés au centime.
- Donner une mémoire à l'agent et le faire chercher dans des documents, avec des citations vérifiables.
- Protéger les actions irréversibles : refus par défaut, veto, approbation humaine, journal infalsifiable.
- Mesurer l'agent sur un jeu de cas et bloquer une version moins bonne avant qu'elle parte en production.
- Chiffrer ce que coûte une tâche et tenir la charge.

## Règles du code

- Bibliothèque standard seulement, annotations modernes (`list[int]`, `X | None`).
- Une entrée invalide lève `ValueError` ; une métrique sans dénominateur renvoie `None` et n'entre pas dans les moyennes.
- Tout est déterministe : le hasard passe par un `random.Random(graine)` local, l'heure par une horloge simulée (`Horloge`).
- Montants en AED, ou en USD avec la conversion 3,6725 ; les clients s'appellent C-1, C-2… ; les chiffres qui ne viennent pas d'un texte officiel sont illustratifs.
