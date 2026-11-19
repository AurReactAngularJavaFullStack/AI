```
JEV 

C le nouveau truc probabilité ds l choix multiples qui peuvent s'imposer là c un ancien de open ai qui a  fondé ça 

Par exemple gestion de sfactrues btp est-ce que l'on demande remboursement client à cause d'impayé via caution bancaire ou on continue en faisant du bfr besoin en fond de roulement ou avance de paiement ou on accepte retard de paiement avec interet ou on demande une ristourne sur certains futures travaux et le jev en fonction des proba des meilleurs choix va faire le best choice 
```

Jev ne choisit pas le meilleur montage financier. 

Il renvoie une probabilité pour chaque option d’une question fermée que vous avez écrite. Le meilleur choix, en euros, se calcule ensuite dans le code, avec l’utilité espérée déjà au parcours.

Jev est le modèle de décision de TypeSafe, lancé par Diogo Almeida, ancien d’OpenAI (il a travaillé sur l’alignement qui a mené à ChatGPT). 

On lui donne un état — le dossier de facture, le courrier, le contrat — et des questions bornées. 

Il ne rédige pas de texte. 

Il répond en parallèle, et chaque réponse est une loi de probabilité :

- **Choice** : une option parmi la liste que vous fournissez, plus la probabilité de chacune.
- **Score** : une position sur une échelle ordonnée.
- **Noul** : une probabilité oui/non.

Les questions d’un même appel ne se voient pas entre elles. « Est-ce un litige ? » et « quelle suite, sachant que c’est un litige ? » sont deux appels, ou un branchement dans le code.

## Le chantier

Cinq suites possibles pour une facture impayée : appeler la caution bancaire, porter le creux en besoin en fonds de roulement, demander une avance, accepter le retard contre intérêts, échanger une ristourne sur de futurs travaux. Jev peut classer la situation. Il ne sait pas ce que chacune coûte.

Le code possède les nombres : montant dû, jours de retard, taux du portage, intérêts prévus au contrat, coût d’appel de la caution, marge des travaux futurs. 

Jev peut fournir des probabilités de jugement, une fois mesurées sur vos propres dossiers étiquetés : « litige plutôt que simple retard de trésorerie », « paiement sous 30 jours vu les courriers », « le client conteste les quantités ».

L’utilité espérée d’une suite \(a\), déjà à l’étape 38, est
$$
EU(a) = \sum_o P(o \mid a)\, U(o)
$$

$$
P(o \mid a)\
$$

 est la probabilité d’une issue si l’on choisit cette suite. 

\(
$$
U(o)
$$
\) est son résultat en euros, calculé sur le grand livre.

La suite retenue est celle dont cette somme est la plus haute. 

Une probabilité Jev n’entre dans \(
$$
P(o \mid a)
$$
\) que si la question portait vraiment sur cette issue. 

Si la question était « laquelle de ces cinq suites est la meilleure ? », les probabilités disent à quel point le texte ressemble à chaque libellé. 

Elles ne sont pas des euros.

Esquisse, chiffres fictifs, pour voir le mécanisme. 

Facture de 100 000 €, 60 jours de retard. 

Porter 90 jours de plus à 8 % l’an coûte environ 2 000 €, quoi qu’il arrive. 

Accepter le retard avec 10 % d’intérêts rapporte ces intérêts seulement si le client paie. 

Appeler la caution peut rapporter 100 000 € et peut faire perdre un chantier dont la marge future est de 40 000 €. 

La ristourne cède de la marge certaine contre une chance de garder le client. On écrit les cinq sommes, on prend le maximum. 

Le score de risque de l’étape 67 passe ensuite : l’appel de caution est irréversible, donc veto et approbation humaine, même si son utilité espérée est la plus haute. Jev ne déclenche pas la caution.

Avant de couper à un seuil, le score de Brier et l’erreur de calibration se mesurent sur vos factures, pas sur un classement public. 

Un 0,90 qui n’est juste que sept fois sur dix ne se traite pas comme un 0,90. 

Les comparaisons publiées en 2026 donnent souvent Jev comme le moins cher et le mieux calibré de cette famille. 

Sur le nombre d’erreurs, un modèle génératif peut faire mieux. 

La calibration se refait sur le corpus BTP.

## Place dans l’agent

Jev est une dépendance facultative, du même rang qu’un classifieur. Il remplace un prompt qui devait deviner une étiquette et qu’il fallait ensuite analyser. Il ne remplace ni la boucle, ni le grand livre, ni le garde-fou. Le parcours a déjà les pièces : softmax pour lire une loi sur des options, utilité espérée pour choisir, Brier pour croire le pourcentage, valeur de l’information pour décider si un renseignement de plus vaut son coût, veto pour l’irréversible.

En faire la même série d’affiches que pour les dix-huit classes n’est pas la priorité. Un seul exemple chiffré, facture BTP, probabilités d’un côté et euros de l’autre, suffit à fixer la frontière. L’entreprise de travaux l’adoptera pour des milliers de petits classements, à condition que l’argent et la caution restent dans son code.

```
En faire la même série d’affiches que pour les dix-huit classes n’est pas la priorité. Un seul exemple chiffré, facture BTP, probabilités d’un côté et euros de l’autre, suffit à fixer la frontière. 

L’entreprise de travaux l’adoptera pour des milliers de petits classements, à condition que l’argent et la caution restent dans son code.Sur le nombre d’erreurs, un modèle génératif peut faire mieux. 

Dc ça veut dire que JEV est facultatif et optionnel pas prioritaire ds ce acs ça a un cout et ça fait predre du temps et quels modèles génératifs st mieux?
```

Jev est facultatif pour le choix caution, fonds de roulement, avance, intérêts ou ristourne. 

Le prix de l’appel n’est pas ce qui le rend secondaire : il est bon marché et rapide. 

Ce qui coûte, c’est un second fournisseur et un jeu de factures étiquetées, pour une décision rare dont les euros sont déjà dans votre code.

À l’unité, Jev facture 0,042 $ par million de jetons d’entrée, et la sortie ne coûte rien. 

Un appel dure en général quelques dixièmes de seconde. 

Dans le test public de novembre 2026 qui l’a comparé à Claude Haiku 5.5, mille décisions Jev revenaient à environ 1 à 2 centimes, contre environ 6 à 7 centimes pour Haiku, et Haiku mettait environ dix fois plus de temps. 

Ajouter Jev ne ralentit donc pas le classement. 

Le ralentissement, c’est l’intégration, puis la mesure de calibration sur vos dossiers, avant de croire un pourcentage.

Il devient prioritaire seulement quand la même question fermée revient des milliers de fois : type de document, litige ou simple retard, facture à relire par un humain. 

Là, le classement borné se rembourse. 

Pour une caution bancaire, le veto et l’approbation humaine restent dans le code, avec ou sans Jev.

Sur le nombre d’erreurs, un modèle génératif peut faire mieux, et un seul test ne désigne pas un gagnant définitif.

- Sur 600 réponses du même test de novembre 2026, Claude Haiku 5.5 s’est trompé 15 fois, l’API Decisions d’OpenAI 30 fois, Jev 41 fois. L’écart était surtout sur les cas faciles et moyens. Sur les cas difficiles, les trois étaient trop proches pour qu’on les départage. Haiku ne renvoie pas de probabilité : il donne une étiquette, pas un nombre à multiplier par des euros.
- Sur 400 textes d’un autre relevé, du 14 novembre 2026, le modèle génératif GPT-6 Luna a fait 81,5 % de bon routage d’intentions, Jev 81,0 %, le modèle de décision de Gemini 81,2 %. Écart trop faible pour changer une architecture. Sur les questions oui/non, Jev était devant les deux API de décision de ce relevé.

Aucun de ces chiffres n’a été mesuré sur des factures de chantier. Le modèle qui se trompe le moins sur des textes généraux n’est pas automatiquement celui qui estime le mieux « le client paiera sous 30 jours ». Cette probabilité se contrôle sur vos dossiers, avec le score de Brier, avant d’entrer dans l’utilité espérée. Sans cette mesure, ni Jev ni Haiku ni GPT ne choisissent le bon montage.