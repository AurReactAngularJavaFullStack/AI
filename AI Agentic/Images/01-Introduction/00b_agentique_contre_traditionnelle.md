# Fiche 00b_agentique_contre_traditionnelle — IA agentique et IA traditionnelle

> Image : `00b_agentique_contre_traditionnelle.jpg` · Ouvrir l'image à gauche et lire ce texte à droite · Leçon complète : [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)

**Une réponse, ou une boucle jusqu'au but**


## Ce que montre l'image

À gauche, l'IA traditionnelle : une question entre, le modèle répond une fois. Pas de plan, pas d'outil, pas de mémoire, un seul tour.

À droite, l'IA agentique part d'un but (« réserver un voyage sous 15 000 »), puis tourne : comprendre le but, planifier, raisonner, appeler des outils, observer, recommencer, jusqu'à un résultat accompagné d'une explication.

Le tableau du bas oppose les deux sur huit lignes : but, plan, raisonnement, outils, mémoire, style d'échange, complexité, sortie.

## Ce que c'est

La phrase du bas de l'affiche est le critère : l'IA traditionnelle produit une réponse, l'IA agentique mène une action. Un système est agentique quand il comprend un but, planifie, raisonne, utilise des outils, garde un contexte et itère.

## Effets et impacts

- Un seul tour suffit pour une question fermée. Il échoue dès que la réponse dépend d'un outil ou d'un résultat intermédiaire.
- La boucle de droite est exactement la définition de l'étape 1 : percevoir, décider, agir, observer, s'arrêter.
- Chaque tour supplémentaire multiplie le coût (fiche 16) et multiplie les chances d'échec (fiche 29).

## Exemple

« Quels sont les lieux à voir à Pune ? » se traite à gauche. « Réserve le voyage à Pune la semaine prochaine, budget 15 000, et confirme l'hôtel » ne se traite qu'à droite : chercher, comparer, appeler, vérifier, puis répondre.

## Dans le cours

- [Étape 1 — L'agent et la fiabilité composée](<../../01-Agent/01-Agent-Definitions-Fondamentaux.md>)
