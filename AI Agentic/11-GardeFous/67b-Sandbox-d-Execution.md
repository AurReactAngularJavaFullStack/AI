# Étape 67 bis — Garde-fous — Sandbox d'exécution

**Dossier :** 11-GardeFous  
**Métiers concernés :** AI Agent Ops, AI Engineers, Forward-Deployed Engineers, AI Platform Team

> Étape 67 bis du parcours · Prérequis : [Score de risque](<67-GardeFous-Formule-Score-de-Risque.md>) · Suite : [Notation de Kendall](<../12-Production-Couts-Optimisation/68-Notation-de-Kendall.md>)

Un agent qui sait écrire du code finit par vouloir l'exécuter : pour additionner les lignes d'un relevé, recalculer une TVA, agréger un fichier de sinistres. Ce code n'a été relu par personne. Il a été écrit par un modèle qui a peut-être lu un document piégé (étape 66), ou fourni tel quel par un utilisateur. L'exécuter dans le processus de l'agent revient à lui donner les clés de l'agent : ses variables d'environnement, ses fichiers, son réseau. Ce fichier construit, en bibliothèque standard, l'outil `executer_python` d'un agent : un sous-processus isolé, borné en temps et en sortie, sans aucune variable du parent, dans un dossier jetable. Il explique aussi pourquoi un filtre sur le texte du code ne constitue pas une frontière de sécurité, et ce que valent des couches d'isolation empilées.

## Définition

Une **sandbox d'exécution** (bac à sable) est un environnement où l'on exécute un code non fiable en ne lui accordant que les droits strictement nécessaires, sous des limites de temps, de mémoire et de taille de sortie, de sorte que le pire qu'il puisse faire reste confiné. C'est l'application du **principe du moindre privilège** : moins on donne de droits, moins il y a d'effets possibles, parce que l'ensemble des actions atteignables ne peut que grandir quand on ajoute un droit. L'isolation se construit en **couches** de solidité croissante : un processus séparé, qui partage le noyau de la machine ; un conteneur, qui ajoute des espaces de noms, des quotas et un filtrage des appels système (seccomp sous Linux) ; une micro-machine virtuelle, qui apporte son propre noyau. On y ajoute un système de fichiers sur liste blanche (un dossier temporaire, rien d'autre), l'interdiction du réseau et un environnement vide. Un contrôle du texte du code, par exemple l'analyse de ses `import`, n'est **pas** une couche d'isolation : c'est une commodité qui donne un message clair au modèle, et il faut la traiter comme telle.

## Rôle dans un agent

La sandbox intervient à l'étape « agir » de la boucle percevoir → décider → agir → observer. Le modèle décide d'appeler l'outil `executer_python` avec un code ; la porte de politique de l'étape 66 dit si ce rôle a droit à cet outil ; le score de risque de l'étape 67 décide si l'appel peut partir seul. C'est la sandbox qui rend ce score raisonnable : sans elle, exécuter un code inconnu est une action **irréversible** (il peut effacer, envoyer, modifier) ; avec elle, ses effets restent dans un dossier détruit à la fin, et l'action se rapproche d'une simple lecture. À l'étape « observer », la sandbox renvoie au modèle un **verdict** (ok, erreur, délai dépassé, sortie tronquée, refus) et une sortie plafonnée : le modèle lit ce qui s'est passé et se corrige, exactement comme avec le `isError` d'un outil MCP (étape 46). Le délai empêche une boucle infinie de figer l'agent, comme le timeout d'un outil à l'étape 12, et le plafond empêche un programme bavard de remplir le contexte et la facture de tokens (étape 72).

## Équation complète

Le verdict d'une exécution, dont les cas se lisent de haut en bas, le premier vrai l'emportant :

$$
v =
\begin{cases}
\text{refus} & \text{si } \Phi(c) \ne \varnothing \\
\text{délai dépassé} & \text{si } t \ge t_{max} \\
\text{sortie tronquée} & \text{si } N > B \\
\text{erreur} & \text{si } r \ne 0 \\
\text{ok} & \text{sinon}
\end{cases}
$$

Le plafond de sortie : ce que le parent garde, et quand la sortie est déclarée tronquée.

$$
G = \min(N,\; B)
$$

$$
\text{tronquée} \iff N > B
$$

La durée pendant laquelle l'agent peut rester bloqué sur une exécution :

$$
D \le t_{max} + t_{arret} + 2\, t_{join}
$$

La défense en profondeur : probabilité qu'une tentative d'évasion franchisse toutes les couches, si les franchissements sont indépendants, puis sans aucune hypothèse.

$$
P_{evasion} = \prod_{i=1}^{m} \varepsilon_i
$$

$$
\max\left(0,\; \sum_{i=1}^{m} \varepsilon_i - (m - 1)\right) \;\le\; P_{evasion} \;\le\; \min_{1 \le i \le m} \varepsilon_i
$$

## Décryptage des symboles

$$
c
$$

Le code soumis à la sandbox, un texte Python écrit par le modèle ou fourni par un utilisateur ; argument `code`.

$$
\Phi(c)
$$

L'ensemble des motifs de refus que la politique trouve dans le texte du code (import hors liste blanche, nom interdit) ; vide si le code est accepté ; fonction `motifs_de_refus(code)`, qui renvoie une liste triée.

$$
t,\quad t_{max}
$$

La durée réelle de l'exécution, en secondes, et le délai au-delà duquel le processus est arrêté, ici 2 s ; constante `DELAI_S`, argument `delai_s`. Le symbole T n'est pas utilisé, parce qu'il désigne la température depuis l'étape 2.

$$
N,\quad B,\quad G
$$

Le nombre d'octets que le programme écrit, ou tente d'écrire, sur un flux (sortie standard ou erreur standard) ; le plafond par flux, ici 4 096 octets (`PLAFOND_OCTETS`, argument `plafond_octets`) ; le nombre d'octets gardés par le parent, `len(lecteur.gardes)`, exposé dans `Execution.octets_gardes`. N n'est jamais stocké au-delà de B.

$$
r
$$

Le code retour du processus, un entier : 0 pour une fin normale, 1 pour une exception Python non rattrapée, une autre valeur quand le processus a été arrêté (1 sous Windows, −9 sous POSIX) ; variable `code_retour`.

$$
v
$$

Le verdict, un texte parmi « refus », « délai dépassé », « sortie tronquée », « erreur », « ok » ; le refus vient de `RefusPolitique`, les quatre autres de `classer(delai_depasse, tronquee, code_retour)`.

$$
D,\quad t_{arret},\quad t_{join}
$$

La durée maximale pendant laquelle l'agent attend la sandbox, puis les deux attentes bornées qui suivent un dépassement : l'attente de la fin du processus après l'ordre d'arrêt, et l'attente de chaque thread lecteur ; toutes deux plafonnées à 5 s par `ATTENTE_ARRET_S`.

$$
m,\quad \varepsilon_i
$$

Le nombre de couches d'isolation, et la probabilité qu'une tentative d'évasion franchisse la couche i, un réel dans [0 ; 1] ; liste `eps`, de longueur m. Les valeurs de ce fichier sont **illustratives** : aucune n'est une mesure.

$$
P_{evasion}
$$

La probabilité qu'une tentative franchisse toutes les couches ; `evasion_independante(eps)` sous l'hypothèse d'indépendance, `bornes_frechet(eps)` sans hypothèse.

## Démonstration

### 1. Le plafond tient : le parent ne garde jamais plus de B octets

Notons n le nombre d'octets lus sur un flux après un certain nombre de lectures, et G le nombre d'octets gardés. On montre par récurrence que G = min(n, B) après chaque lecture. Au départ, n = 0 et G = 0 = min(0, B). Supposons G = min(n, B), et lisons un bloc de ℓ octets ; le code en garde min(ℓ, place), avec place = max(0, B − G). Deux cas se présentent. Si n ≥ B, alors G = B, la place est nulle, rien n'est ajouté, et G = B = min(n + ℓ, B). Si n < B, alors G = n, la place vaut B − n, et G devient n + min(ℓ, B − n) = min(n + ℓ, B). Dans les deux cas, la propriété se transmet. À la fin du flux, n = N et l'on obtient l'égalité G = min(N, B).

Le drapeau « tronquée » se lève à la première lecture où ℓ dépasse la place restante, c'est-à-dire exactement quand le total lu dépasse B : tronquée ⟺ N > B. La mémoire du parent est donc bornée **quel que soit N** : au plus B octets gardés, plus un bloc en cours de lecture (65 536 octets), soit 69 632 octets par flux et moins de 140 Kio pour les deux. À l'inverse, `proc.communicate()` garde toute la sortie en mémoire : un programme qui écrit 10 Go coûterait 10 Go à l'agent. Dans le programme, le code prévu pour écrire 2 000 000 d'octets laisse G = 4 096 octets, tous des « x ».

Le lecteur fait une chose de plus : au premier octet de trop, il **arrête le producteur**. Il ne s'agit pas seulement d'économiser la mémoire, mais aussi le temps de calcul : sans cet arrêt, un programme qui écrit sans fin tournerait jusqu'au délai, et le parent passerait ce temps à lire puis jeter des octets.

### 2. L'agent reprend la main en un temps borné

L'attente `proc.wait(timeout=delai_s)` rend la main au plus tard à t_max. Si le délai est dépassé, `tuer` envoie un ordre que le programme **ne peut pas intercepter** : `TerminateProcess` sous Windows, `SIGKILL` sous POSIX. Ce point compte : un programme peut ignorer une interruption polie, car il lui suffit d'attraper `KeyboardInterrupt` ou d'installer un gestionnaire de `SIGTERM`, mais aucun code du programme ne s'exécute après ces deux ordres, pas même un bloc `finally`. On attend ensuite la fin du processus au plus t_arrêt = 5 s, puis chaque thread lecteur au plus t_join = 5 s. Chaque attente étant bornée, la somme l'est :

$$
D \le 2 + 5 + 2 \times 5 = 17 \text{ s}
$$

C'est une borne de pire cas : dans le programme, l'agent reprend la main un instant après les 2 s de la boucle infinie. Sur une boucle d'agent de E étapes qui exécutent chacune un code, l'attente totale est au plus E × D, ce qui garantit qu'une session ne reste jamais suspendue à un programme qui ne finit pas. Les deux flux sont lus par deux threads, pour la raison démontrée à l'[étape 46](<../09-MCP/46-MCP-Definitions-Fondamentaux.md>), point 4 : un tube plein bloquerait le programme, puis le parent.

### 3. Un filtre sur le texte du code n'est pas une frontière

La politique du programme n'accepte que les `import` d'une liste blanche (`math`, `json`, `re`…) et refuse une courte liste de noms comme `eval`, `exec` et `open`. Un tel contrôle repère le code maladroit et donne au modèle un message clair, mais il ne garantit rien, pour deux raisons.

D'abord il est **incomplet**. Il raisonne sur le texte, or une même intention s'écrit d'une infinité de façons : un nom peut être reconstruit à l'exécution à partir de morceaux que l'analyse statique ne rapproche pas. Le programme contient un exemple, `CODE_CONTOURNEMENT`, qui obtient un module hors de la liste blanche sans qu'aucun `import` interdit ni aucun nom interdit n'apparaisse dans le source : `motifs_de_refus` le déclare donc accepté. On ne cherche pas ici à lister les variantes ; le point est qu'elles existent et qu'un filtre à motifs en manquera toujours, exactement comme le détecteur d'injection de l'[étape 66](<66-GardeFous-Definitions-Fondamentaux.md>), point 5.

Ensuite il est **trop strict** : refusant sur la présence d'un mot, il rejette un code inoffensif où ce mot n'est jamais exécuté, comme un `import os` placé dans une branche `if False`. Un contrôle à la fois incomplet et trop strict ne peut pas servir de frontière.

La garantie vient donc d'ailleurs, et c'est ce que montre la section 3 du programme. Le code de contournement charge bien le module, mais ce module ne lui sert à rien : l'environnement du sous-processus est **vide**, si bien qu'une clé secrète présente chez le parent (`CLE_API_DEMO`) ne figure pas chez l'enfant, et le dossier courant ne contient **que** `programme.py`, le fichier qu'on vient d'y écrire. L'évasion de la couche 1 n'ouvre sur rien, parce que les couches 2 et 3 ne dépendent pas du texte du code. On garde le filtre pour le message qu'il donne au modèle, jamais comme protection.

### 4. L'isolement vient du processus, pas du texte

Trois décisions font l'isolement, et aucune ne lit le code. Le sous-processus est lancé avec un **environnement vide** (`env={}`, à l'exception de `SYSTEMROOT`, la seule variable que Windows exige pour démarrer un interpréteur) : aucune clé d'API, aucun proxy, aucun `PATH` du parent n'est transmis. Il tourne dans un **dossier temporaire jetable**, créé par `tempfile.TemporaryDirectory`, qui devient son dossier courant et qui est détruit à la fin, de sorte que les fichiers écrits ne survivent pas et ne touchent pas le reste du disque. Il est lancé avec l'option `-I` (mode isolé) : l'interpréteur ignore les variables `PYTHON*` et n'ajoute pas le dossier courant au chemin d'import, ce qui empêche un fichier déposé à côté de se faire charger à la place d'un module standard. Sous POSIX, `preexec_fn` pose en plus des limites de mémoire et de temps CPU (`setrlimit`), et `start_new_session` place l'enfant dans son propre groupe pour que `SIGKILL` emporte aussi ses éventuels enfants. Ce que ce code **ne fait pas**, il faut le dire : il ne coupe pas l'accès réseau et ne filtre pas les appels système, parce que la bibliothèque standard ne le permet pas de façon portable. Un vrai déploiement ajoute pour cela un conteneur ou une micro-VM ; le code de ce fichier est la première couche, honnête sur ses limites.

### 5. La défense en profondeur se multiplie, mais seulement si les couches sont indépendantes

Empiler m couches dont chacune est franchie avec la probabilité εᵢ donne, si les franchissements sont **indépendants**, une probabilité d'évasion totale égale au produit, parce que la probabilité d'une intersection d'événements indépendants est le produit de leurs probabilités (même raisonnement qu'à l'[étape 49](<../09-MCP/49-MCP-Formule-Score-de-Disponibilite.md>), point 5, pour la disponibilité en parallèle). Avec les valeurs illustratives 1, 0,1, 0,01 et 0,001 — une couche politique qui ne protège de rien (ε = 1), puis un processus, un conteneur et une micro-VM de plus en plus durs à franchir —, le produit vaut 10⁻⁶. La couche politique, parce que son ε vaut 1, ne change pas le produit : c'est l'écriture chiffrée du fait qu'un filtre contournable n'ajoute aucune sécurité.

Mais l'indépendance est une hypothèse, souvent fausse : deux couches qui partagent le même noyau tombent ensemble sur une faille de ce noyau. Sans aucune hypothèse, les inégalités de Fréchet encadrent la probabilité : elle vaut au plus le plus petit des εᵢ, et au moins max(0, Σεᵢ − (m − 1)). La borne haute min εᵢ dit l'essentiel : **le montage n'est jamais plus sûr que sa meilleure couche**, et une faille commune à deux couches peut porter P(franchir les deux) bien au-dessus du produit, par exemple à 0,005 là où le produit donnait 0,0002. C'est pourquoi on cherche des couches de natures différentes (un processus, puis un noyau différent dans une micro-VM), qui ont peu de chances de partager la même faille.

### 6. Exemple fait à la main (le code reprend ces nombres)

| Cas | Entrée | Verdict | Grandeur vérifiée |
|---|---|---|---|
| bénin | mensualité 1 M AED, 4,5 %, 300 mois | ok | sortie 5558.32, code retour 0 |
| boucle infinie | `while True: pass` | délai dépassé | 0 octet gardé, processus arrêté et attendu |
| import interdit | `import socket` | refus | jamais exécuté (politique) |
| sortie énorme | 2 000 000 d'octets | sortie tronquée | 4 096 octets gardés, arrêté avant la fin |
| erreur | `print(1 / 0)` | erreur | code retour 1, ZeroDivisionError |

| Grandeur | Calcul | Résultat |
|---|---|---|
| mensualité | 1 000 000 × 0,00375 / (1 − 1,00375⁻³⁰⁰) | 5 558,32 AED |
| mémoire par flux | 4 096 + 65 536 | 69 632 octets |
| borne d'attente | 2 + 5 + 2 × 5 | 17 s |
| évasion, indépendance | 1 × 0,1 × 0,01 × 0,001 | 10⁻⁶ |
| borne haute de Fréchet | min(1 ; 0,1 ; 0,01 ; 0,001) | 0,001 |

## Effets et comportement

- **Le délai borne le temps, le plafond borne la mémoire et le contexte.** Sans délai, une boucle infinie fige l'agent ; sans plafond, un programme bavard remplit la mémoire du parent et la facture de tokens.
- **Un verdict, pas une exception qui remonte.** La sandbox renvoie au modèle un mot (ok, erreur, délai, tronquée, refus) et une sortie courte, que le modèle lit pour se corriger, comme un `isError` MCP.
- **L'arrêt est non interceptable.** `SIGKILL` et `TerminateProcess` ne laissent s'exécuter aucun code du programme ; c'est ce qui garantit la borne de temps, mais aussi qu'un `finally` du code sandboxé ne tourne pas après un dépassement.
- **Le filtre de texte sert le message, pas la sécurité.** Il aide le modèle à comprendre un refus ; l'isolement vient du processus séparé, de l'environnement vide et du dossier jetable.
- **Les couches ne se multiplient que si elles sont indépendantes.** Une faille de noyau commune fait tomber ensemble le processus et le conteneur ; on vise des couches de natures différentes.

## Du symbole au code Python

$$
\Phi(c)
$$

**Variable ou fonction :** `motifs_de_refus(code)`, et l'exception `RefusPolitique`

$$
G = \min(N,\; B)
$$

**Variable ou fonction :** `LecteurBorne` (champ `gardes`, drapeau `tronque`), `Execution.octets_gardes`

$$
v
$$

**Variable ou fonction :** `classer(delai_depasse, tronquee, code_retour)`, et `executer_isole(...)` qui renvoie un `Execution`

$$
t_{max},\quad B
$$

**Variable ou fonction :** `DELAI_S`, `PLAFOND_OCTETS`, arguments `delai_s` et `plafond_octets`

$$
\text{arrêt non interceptable}
$$

**Variable ou fonction :** `tuer(proc)` (`os.killpg` + `SIGKILL` sous POSIX, `proc.kill()` sous Windows)

$$
\prod_i \varepsilon_i,\qquad \text{bornes de Fréchet}
$$

**Variable ou fonction :** `evasion_independante(eps)`, `bornes_frechet(eps)`

### Déroulé, ligne par ligne

**La politique (couche 1).** `MODULES_AUTORISES` est la liste blanche des modules, `NOMS_INTERDITS` les noms refusés. `motifs_de_refus(code)` analyse l'arbre syntaxique avec `ast.parse` : une erreur de syntaxe donne un motif « syntaxe invalide » ; sinon, chaque `import`/`from … import` dont le module n'est pas dans la liste blanche, et chaque `ast.Name` d'un nom interdit, ajoutent un motif. La fonction renvoie la **liste triée** des motifs, vide si le code est accepté, ce qui rend la sortie reproductible. On retient deux défauts, démontrés au point 3 : la fonction accepte `CODE_CONTOURNEMENT`, et elle refuse un `import os` placé sous `if False`.

**Le lecteur borné (plafond de sortie).** `LecteurBorne` démarre un thread qui lit le flux par blocs de 65 536 octets (`read1`). Il garde au plus `plafond` octets dans `gardes` (`place = max(0, plafond - len(gardes))`), de sorte que l'invariant `len(gardes) <= plafond` tient toujours (point 1). Au premier bloc qui dépasse la place, il lève le drapeau `tronque` et appelle `trop_plein`, qui est `lambda: tuer(proc)` : le producteur est arrêté. `texte()` décode les octets gardés en UTF-8, en remplaçant les octets invalides.

**L'arrêt (`tuer`).** Si le processus est déjà fini (`poll()` non `None`), on ne fait rien. Sinon, sous POSIX, `os.killpg(proc.pid, SIGKILL)` emporte tout le groupe créé par `start_new_session` ; sous Windows, `proc.kill()` agit sur le handle, non sur un PID qui pourrait avoir été réutilisé. L'`OSError` d'un processus déjà terminé est ignorée.

**`executer_isole(code, ...)`**, le cœur. Elle crée un `TemporaryDirectory`, y écrit `programme.py`, prépare `env` (vide, plus `SYSTEMROOT` sous Windows), puis lance `subprocess.Popen([sys.executable, "-I", "-X", "utf8", programme])` avec `cwd` sur le dossier jetable, `stdin` sur `DEVNULL`, et les deux sorties en tubes. Sous POSIX, `start_new_session=True` et un `preexec_fn` qui pose les limites `setrlimit` ; sous Windows, `CREATE_NEW_PROCESS_GROUP`. Deux `LecteurBorne` vident les tubes. `proc.wait(timeout=delai_s)` attend la fin ; un `TimeoutExpired` lève `delai_depasse`, appelle `tuer`, puis attend encore au plus `ATTENTE_ARRET_S`. On joint les deux threads (bornés), on ferme les tubes, et `termine = proc.poll() is not None` atteste qu'aucun orphelin ne reste. Le verdict vient de `classer`.

**`classer(delai_depasse, tronquee, code_retour)`** applique l'ordre de l'équation : un arrêt imposé par la sandbox (délai, puis troncature) l'emporte sur le code retour qu'il a lui-même provoqué, et seul un code retour 0 sans incident donne « ok ».

**`executer_python(code)`**, l'outil donné au modèle. Il appelle d'abord `motifs_de_refus` : s'il y a des motifs, il lève `RefusPolitique`, et la fonction n'est **jamais** exécutée. Sinon, il appelle `executer_isole` et renvoie un petit dictionnaire `{verdict, sortie (≤ 200 caractères), erreur (dernière ligne)}`, que la boucle d'agent transmet au modèle.

**La défense en profondeur.** `evasion_independante(eps)` renvoie `math.prod(eps)` après avoir vérifié les domaines ; `bornes_frechet(eps)` renvoie `(max(0, somme − (m−1)), min(eps))`.

**`main()`**, section par section. (1) Six essais de politique : `import math` accepté, `import socket` et `from os import path` refusés, `eval` refusé, l'`import os` mort sous `if False` refusé à tort, le contournement accepté à tort. (2) Les cas d'exécution, quatre exécutés et un refusé d'avance : bénin (ok, 5558.32), boucle infinie (délai dépassé, 0 octet), import interdit (refusé par la politique, jamais exécuté), sortie énorme (tronquée, 4 096 octets), erreur (code retour 1). (3) Le contournement : on pose une clé secrète chez le parent, on exécute, et l'on vérifie que l'enfant a chargé le module mais **ne voit ni la clé ni d'autre fichier** que `programme.py`, pendant que le parent, lui, garde sa clé. (4) L'outil dans la boucle d'agent : le premier appel est refusé (le refus repart vers le modèle), le second réussit, le modèle conclut. (5) La défense en profondeur : produit 10⁻⁶, bornes de Fréchet, effet d'un noyau partagé.

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`texte(t)`** — Cette petite fonction est le greffier qui met en forme une réplique du faux modèle : elle reçoit une chaîne de caractères et renvoie un objet `Bloc` de type « text » dont le champ `text` contient cette chaîne, tous les autres champs gardant leur valeur vide par défaut. Elle sert à écrire le script du `FakeLLM` de la section 4 de `main`, où la dernière réponse scriptée, « La mensualité vaut 5 558,32 AED. », est fabriquée ainsi avant d'être relue par `executer_agent` comme la réponse finale de l'agent.

**`appel_outil(nom, arguments, id_)`** — Celle-ci rédige, comme un standardiste qui remplit un bon de commande, la demande d'outil qu'un vrai modèle enverrait : elle reçoit le nom de l'outil, le dictionnaire de ses arguments et un identifiant, puis renvoie un `Bloc` de type « tool_use » qui range ces trois informations dans les champs `name`, `input` et `id`. Dans la section 4, elle fabrique les deux appels à `executer_python`, identifiés « s1 » et « s2 », le premier portant le code qui importe `socket`, le second le calcul bénin de la mensualité.

**`FakeLLM.__init__(script)`** — Le constructeur prépare un comédien qui ne connaît que son texte : il reçoit la liste des réponses prévues, en garde une copie dans `self.script`, pour que le script d'origine ne soit jamais modifié par la suite, et met à zéro le compteur `self.appels` qui dira combien de répliques ont déjà été jouées. Il ne renvoie rien ; il installe seulement l'état grâce auquel le faux modèle restera déterministe et gratuit tout au long de la démonstration.

**`FakeLLM.create(system, messages, tools)`** — Cette méthode imite l'appel d'API d'un modèle de langage, comme un souffleur qui tend au comédien la réplique suivante sans écouter ce qu'on lui dit : elle reçoit, par mots-clés seulement, le prompt système, l'historique des messages et la liste des outils, les ignore, puis renvoie la réponse du script de rang `self.appels` en avançant le compteur d'une unité. Quand le script est épuisé, elle lève une `RuntimeError` au lieu d'inventer une réponse, ce qui fait échouer bruyamment toute boucle qui demanderait un tour de trop.

**`executer_agent(llm, system, question, outils, schemas, max_etapes)`** — C'est la boucle canonique de l'agent, recopiée telle quelle, qui joue le chef de chantier faisant la navette entre le modèle et ses outils : elle reçoit le modèle, le prompt système, la question, le dictionnaire des outils, leurs schémas et un nombre maximal d'étapes, huit par défaut, place la question dans l'historique, puis, à chaque étape, demande une réponse, l'ajoute telle quelle à l'historique, s'arrête sur « refus » ou « tronque » selon la raison d'arrêt, passe au tour suivant sur une pause, et rend « fini » avec le texte final quand aucun appel d'outil ne reste. Sinon, elle s'arrête sur « boucle » si les mêmes appels reviennent deux fois de suite, exécute chaque outil en renvoyant au modèle soit son résultat en JSON, soit l'erreur marquée `is_error`, regroupe tous les résultats dans un seul message et finit sur « max_etapes » si le budget s'épuise ; elle renvoie un dictionnaire avec le statut, la trace et le nombre d'étapes, trois dans la section 4.

**`motifs_de_refus(code)`** — Cette fonction est le douanier de la première couche, celui qui lit les papiers sans fouiller les bagages : elle reçoit le texte du programme, tente de l'analyser avec `ast.parse` et renvoie aussitôt un seul motif « syntaxe invalide » si l'analyse échoue, puis parcourt tous les nœuds de l'arbre pour noter chaque module importé hors de la liste blanche `MODULES_AUTORISES` et chaque nom de `NOMS_INTERDITS` comme `eval` ou `open`. Elle renvoie la liste triée des motifs, vide quand le code est accepté ; `main` montre qu'elle refuse `import socket` et `eval`, mais aussi, à tort, un `import os` mort sous `if False`, et qu'elle laisse passer le contournement par `getattr`.

**`LecteurBorne.__init__(flux, plafond, trop_plein)`** — Le constructeur poste une sentinelle à la sortie d'un tuyau : il reçoit le flux à vider, le plafond d'octets à garder et la fonction à appeler en cas de débordement, range ces trois éléments, prépare un tampon `gardes` vide et un drapeau `tronque` baissé, puis crée et démarre aussitôt un thread démon qui exécutera `_boucle`. Il ne renvoie rien, mais dès sa sortie le tube est lu en continu, ce qui empêche le programme sandboxé de se bloquer sur un tuyau plein ; `executer_isole` en crée deux, un pour la sortie standard et un pour les erreurs.

**`LecteurBorne._boucle()`** — Cette méthode est le travail même de la sentinelle, qui tourne dans son thread jusqu'à la fin du flux : à chaque tour, elle lit avec `read1` au plus 65 536 octets disponibles, s'arrête dès qu'elle reçoit un bloc vide, calcule la place restante sous le plafond et n'ajoute au tampon que ce qui y tient, si bien que la longueur gardée ne dépasse jamais le plafond. Au premier bloc qui déborde, elle lève le drapeau `tronque` une seule fois et appelle `trop_plein`, qui arrête le producteur au lieu de stocker le reste ; avec le plafond de 4 096 octets, la sortie énorme de 2 000 000 d'octets est ainsi coupée net.

**`LecteurBorne.texte()`** — Cette méthode est le traducteur qui rend lisible le contenu du tampon : elle prend les octets gardés, les décode en UTF-8 en remplaçant par un caractère de substitution tout octet invalide, ce qui arrive quand la coupure tombe au milieu d'un caractère, puis remplace chaque fin de ligne Windows, un retour chariot suivi d'un saut de ligne, par un simple saut de ligne. Elle renvoie la chaîne obtenue, que `executer_isole` place dans les champs `sortie` et `erreurs` de l'`Execution`, de sorte que le même texte sorte sous Windows comme sous POSIX.

**`tuer(proc)`** — Cette fonction est le disjoncteur de la sandbox, celui qui coupe le courant sans demander l'avis de la machine : elle reçoit un processus lancé par `subprocess.Popen`, ne fait rien s'il est déjà terminé, sinon envoie sous POSIX un `SIGKILL` à tout le groupe de processus créé par `start_new_session`, enfants compris, et appelle sous Windows `proc.kill()`, qui agit sur le handle et non sur un PID qu'un autre processus aurait pu reprendre. Elle ne renvoie rien et avale l'`OSError` d'un processus mort entre-temps ; comme aucun de ces deux arrêts ne laisse tourner le moindre code du programme, c'est elle qui garantit la borne de temps et le plafond de sortie.

**`_limites_posix(memoire_octets, cpu_s)`** — Cette fonction est le règlement intérieur qu'on affiche dans la cellule juste avant d'y faire entrer le programme : exécutée dans l'enfant, sous POSIX seulement, au moment du `preexec_fn`, elle reçoit un plafond de mémoire et un temps CPU, puis tente de poser trois limites avec `setrlimit`, l'espace d'adresses (256 Mio par défaut dans `executer_isole`), le temps CPU (le délai tronqué à l'entier plus une seconde, soit 3 s pour le délai de 2 s) et la taille des fichiers écrits, 1 Mio. Elle ne renvoie rien et ignore silencieusement une limite que le système refuserait, si bien qu'elle durcit l'isolement là où c'est possible sans jamais faire échouer le lancement.

**`classer(delai_depasse, tronquee, code_retour)`** — Cette fonction est l'arbitre qui rend le verdict après le match, selon un ordre de préséance fixé d'avance : elle reçoit deux drapeaux, délai dépassé et sortie tronquée, ainsi que le code retour du processus, et renvoie « délai dépassé » si le premier est levé, sinon « sortie tronquée » si le second l'est, sinon « erreur » pour tout code retour différent de 0, et « ok » seulement dans le dernier cas. Cet ordre fait qu'un arrêt imposé par la sandbox l'emporte sur le code retour non nul qu'il a lui-même provoqué, et c'est ce mot que `executer_isole` range dans le champ `verdict`.

**`evasion_independante(eps)`** — Cette fonction calcule la probabilité qu'un évadé franchisse tous les murs d'une forteresse quand chaque mur tient indépendamment des autres : elle reçoit la liste des probabilités de franchissement εᵢ, lève `ValueError` si la liste est vide ou si l'une d'elles sort de [0 ; 1], puis renvoie leur produit par `math.prod`. Avec les valeurs illustratives 1 ; 0,1 ; 0,01 ; 0,001, elle rend 10⁻⁶, et le même nombre sans la couche politique, ce que `main` vérifie pour montrer qu'un filtre contournable, dont ε vaut 1, n'ajoute aucune sécurité.

**`bornes_frechet(eps)`** — Celle-ci est l'experte prudente qui refuse de supposer les murs indépendants : elle reçoit la même liste de probabilités et renvoie le couple formé par la borne basse de Fréchet, max(0, Σεᵢ − (m − 1)) pour m couches, et la borne haute, le plus petit des εᵢ. Pour les quatre couches de la section 5, elle rend 0 et 0,001, ce qui rappelle que le montage n'est jamais plus sûr que sa meilleure couche ; sur les deux couches 0,1 et 0,01, sa borne haute de 0,01 laisse la place à une faille de noyau partagée de 0,005, bien au-dessus du produit 0,001.

```python
"""Étape 67 bis — une sandbox d'exécution en bibliothèque standard : sous-processus isolé, délai, plafonds, politique."""
import ast
import json
import math
import os
import signal
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass, field

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- port LLM et boucle (code canonique, recopié tel quel)
@dataclass
class Bloc:
    type: str                      # "text" ou "tool_use"
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class Reponse:
    stop_reason: str               # "end_turn", "tool_use", "max_tokens", "refusal", "pause_turn"
    content: list


def texte(t: str) -> Bloc:
    return Bloc(type="text", text=t)


def appel_outil(nom: str, arguments: dict, id_: str) -> Bloc:
    return Bloc(type="tool_use", id=id_, name=nom, input=arguments)


class FakeLLM:
    """Faux LLM scripté : renvoie les réponses prévues, dans l'ordre. Déterministe, gratuit."""

    def __init__(self, script: list):
        self.script = list(script)
        self.appels = 0

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        if self.appels >= len(self.script):
            raise RuntimeError("script épuisé : le faux LLM n'a plus de réponse prévue")
        reponse = self.script[self.appels]
        self.appels += 1
        return reponse


def executer_agent(llm, system: str, question: str, outils: dict, schemas: list, max_etapes: int = 8) -> dict:
    """Boucle percevoir → décider → agir → observer, avec trois arrêts."""
    messages = [{"role": "user", "content": question}]
    trace = []
    precedente = None
    for etape in range(1, max_etapes + 1):
        reponse = llm.create(system=system, messages=messages, tools=schemas)
        messages.append({"role": "assistant", "content": reponse.content})   # tel quel, sans retouche
        if reponse.stop_reason == "refusal":
            return {"statut": "refus", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "max_tokens":
            return {"statut": "tronque", "trace": trace, "etapes": etape}
        if reponse.stop_reason == "pause_turn":
            continue
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if reponse.stop_reason == "end_turn" or not appels:
            final = "".join(b.text for b in reponse.content if b.type == "text")
            return {"statut": "fini", "reponse": final, "trace": trace, "etapes": etape}
        signature = [(b.name, json.dumps(b.input, sort_keys=True)) for b in appels]
        if signature == precedente:           # même action, mêmes arguments, deux fois de suite
            return {"statut": "boucle", "trace": trace, "etapes": etape}
        precedente = signature
        resultats = []
        for b in appels:
            try:
                sortie = outils[b.name](**b.input)
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": json.dumps(sortie, ensure_ascii=False)})
                trace.append((b.name, b.input, sortie))
            except Exception as e:            # l'erreur repart vers le modèle, elle n'est pas avalée
                resultats.append({"type": "tool_result", "tool_use_id": b.id,
                                  "content": f"{type(e).__name__}: {e}", "is_error": True})
                trace.append((b.name, b.input, f"ERREUR {e}"))
        messages.append({"role": "user", "content": resultats})   # tous les résultats dans UN message
    return {"statut": "max_etapes", "trace": trace, "etapes": max_etapes}


# ---------------------------------------------------------------- couche 1 : politique sur le texte du code (commodité, PAS frontière)
MODULES_AUTORISES = frozenset({"math", "statistics", "json", "re", "decimal", "fractions",
                               "itertools", "collections", "datetime"})
NOMS_INTERDITS = frozenset({"__import__", "eval", "exec", "compile", "open", "breakpoint", "input"})


class RefusPolitique(PermissionError):
    pass


def motifs_de_refus(code: str) -> list[str]:
    """Liste triée des motifs de refus ; liste vide = code accepté. Liste blanche des modules, refus par défaut."""
    try:
        arbre = ast.parse(code)
    except SyntaxError as e:
        return [f"syntaxe invalide : {e.msg}"]
    motifs = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            modules = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            modules = [n.module if n.level == 0 and n.module else "(import relatif)"]
        else:
            modules = []
        for m in modules:
            if m.split(".")[0] not in MODULES_AUTORISES:
                motifs.add(f"import non autorisé : {m}")
        if isinstance(n, ast.Name) and n.id in NOMS_INTERDITS:
            motifs.add(f"nom interdit : {n.id}")
    return sorted(motifs)


# ---------------------------------------------------------------- couches 2 et 3 : processus séparé, limites, environnement vide
DELAI_S = 2.0                      # t_max : au-delà, le processus est arrêté
PLAFOND_OCTETS = 4096              # B : octets gardés au plus, par flux
MEMOIRE_OCTETS = 256 * 1024 * 1024  # appliqué sous POSIX seulement (RLIMIT_AS)
ATTENTE_ARRET_S = 5.0              # borne de l'attente après l'arrêt, puis de chaque thread lecteur


class LecteurBorne:
    """Vide un flux dans un thread ; garde au plus `plafond` octets ; au premier octet de trop, appelle `trop_plein`."""

    def __init__(self, flux, plafond: int, trop_plein):
        self.flux = flux
        self.plafond = plafond
        self.trop_plein = trop_plein
        self.gardes = bytearray()
        self.tronque = False
        self.thread = threading.Thread(target=self._boucle, daemon=True)
        self.thread.start()

    def _boucle(self) -> None:
        while True:
            bloc = self.flux.read1(65536)        # rend ce qui est disponible, b"" à la fin du flux
            if not bloc:
                return
            place = max(0, self.plafond - len(self.gardes))
            self.gardes += bloc[:place]          # invariant : len(gardes) <= plafond
            if len(bloc) > place and not self.tronque:
                self.tronque = True
                self.trop_plein()                # on arrête le producteur au lieu de stocker le reste

    def texte(self) -> str:
        return bytes(self.gardes).decode("utf-8", errors="replace").replace("\r\n", "\n")


def tuer(proc: subprocess.Popen) -> None:
    """Arrêt immédiat, sans exécuter de code du programme. POSIX : tout le groupe ; Windows : TerminateProcess."""
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)  # le groupe créé par start_new_session : enfants compris
        else:
            proc.kill()                          # agit sur le handle du processus, pas sur un PID réutilisable
    except OSError:
        pass                                     # déjà terminé entre-temps


def _limites_posix(memoire_octets: int, cpu_s: int) -> None:
    """Exécuté dans l'enfant juste avant le programme (POSIX) : mémoire, temps CPU, taille des fichiers écrits."""
    import resource
    for limite, valeur in ((resource.RLIMIT_AS, memoire_octets), (resource.RLIMIT_CPU, cpu_s),
                           (resource.RLIMIT_FSIZE, 1024 * 1024)):
        try:
            resource.setrlimit(limite, (valeur, valeur))
        except (ValueError, OSError):
            pass


@dataclass
class Execution:
    verdict: str                   # "ok", "erreur", "délai dépassé", "sortie tronquée"
    code_retour: int | None
    sortie: str
    erreurs: str
    octets_gardes: int
    termine: bool                  # le processus a bien été attendu : aucun orphelin


def classer(delai_depasse: bool, tronquee: bool, code_retour: int | None) -> str:
    """Ordre fixe : un arrêt imposé par la sandbox l'emporte sur le code retour qu'il a provoqué."""
    if delai_depasse:
        return "délai dépassé"
    if tronquee:
        return "sortie tronquée"
    if code_retour != 0:
        return "erreur"
    return "ok"


def executer_isole(code: str, delai_s: float = DELAI_S, plafond_octets: int = PLAFOND_OCTETS,
                   memoire_octets: int = MEMOIRE_OCTETS) -> Execution:
    """Lance `code` dans un interpréteur séparé, isolé, dans un dossier temporaire jetable, avec un environnement vide."""
    with tempfile.TemporaryDirectory(prefix="sandbox_", ignore_cleanup_errors=True) as dossier:
        programme = os.path.join(dossier, "programme.py")
        with open(programme, "w", encoding="utf-8") as f:
            f.write(code)
        env: dict[str, str] = {}                 # aucune variable du parent : ni clé d'API, ni proxy, ni PATH
        options: dict = {}
        if os.name == "nt":
            env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", "C:\\Windows")   # seule variable exigée par Windows
            options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            options["start_new_session"] = True
            options["preexec_fn"] = lambda: _limites_posix(memoire_octets, int(delai_s) + 1)
        proc = subprocess.Popen([sys.executable, "-I", "-X", "utf8", programme], cwd=dossier, env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options)
        sortie = LecteurBorne(proc.stdout, plafond_octets, lambda: tuer(proc))
        erreurs = LecteurBorne(proc.stderr, plafond_octets, lambda: tuer(proc))
        delai_depasse = False
        try:
            code_retour = proc.wait(timeout=delai_s)
        except subprocess.TimeoutExpired:
            delai_depasse = True
            tuer(proc)
            code_retour = proc.wait(timeout=ATTENTE_ARRET_S)
        for lecteur in (sortie, erreurs):
            lecteur.thread.join(timeout=ATTENTE_ARRET_S)
        proc.stdout.close()
        proc.stderr.close()
        termine = proc.poll() is not None
    verdict = classer(delai_depasse, sortie.tronque or erreurs.tronque, code_retour)
    return Execution(verdict, code_retour, sortie.texte(), erreurs.texte(), len(sortie.gardes), termine)


def executer_python(code: str) -> dict:
    """L'outil donné au modèle : la politique d'abord, puis l'exécution isolée ; le verdict repart vers le modèle."""
    motifs = motifs_de_refus(code)
    if motifs:
        raise RefusPolitique("; ".join(motifs))
    r = executer_isole(code)
    lignes_err = r.erreurs.strip().splitlines()
    return {"verdict": r.verdict, "sortie": r.sortie.strip()[:200], "erreur": lignes_err[-1] if lignes_err else ""}


# ---------------------------------------------------------------- défense en profondeur
def evasion_independante(eps: list[float]) -> float:
    """P(franchir toutes les couches) si les franchissements sont indépendants : produit des εᵢ."""
    if not eps or any(not 0 <= e <= 1 for e in eps):
        raise ValueError("il faut au moins une couche et des εᵢ dans [0, 1]")
    return math.prod(eps)


def bornes_frechet(eps: list[float]) -> tuple[float, float]:
    """Sans hypothèse d'indépendance : max(0, Σεᵢ − (m − 1)) ≤ P ≤ min εᵢ."""
    return max(0.0, sum(eps) - (len(eps) - 1)), min(eps)


CODE_BENIN = "import math\nr = 0.045 / 12\nprint(round(1_000_000 * r / (1 - math.pow(1 + r, -300)), 2))\n"
CODE_BOUCLE = "while True:\n    pass\n"
CODE_IMPORT = "import socket\nprint(socket.gethostname())\n"
CODE_SORTIE = "for _ in range(2000):\n    print('x' * 1000, end='')\n"
CODE_ERREUR = "print(1 / 0)\n"
CODE_CONTOURNEMENT = ("m = getattr(__builtins__, '__imp' + 'ort__')('o' + 's')\n"
                      "print('module chargé :', m.__name__)\n"
                      "print('clé du parent visible :', 'CLE_API_DEMO' in m.environ)\n"
                      "print('dossier courant :', sorted(m.listdir('.')))\n")


def main() -> None:
    print("1. Politique sur le texte du code (liste blanche de modules, noms interdits)")
    essais = [("import math", "import math"), ("import socket", "import socket"),
              ("from os import path", "from os import path"), ("eval('2 + 2')", "eval('2 + 2')"),
              ("if False: import os", "if False:\n    import os"), ("contournement", CODE_CONTOURNEMENT)]
    for nom, code in essais:
        motifs = motifs_de_refus(code)
        print(f"  {nom:<20} → {'accepté' if not motifs else 'refusé (' + '; '.join(motifs) + ')'}")
    assert motifs_de_refus("import math") == []
    assert motifs_de_refus("import socket") == ["import non autorisé : socket"]
    assert motifs_de_refus("from os import path") == ["import non autorisé : os"]
    assert motifs_de_refus("eval('2 + 2')") == ["nom interdit : eval"]
    assert motifs_de_refus("if False:\n    import os") == ["import non autorisé : os"]   # trop strict
    assert motifs_de_refus(CODE_CONTOURNEMENT) == []           # et incomplet : le contournement passe

    print(f"2. Quatre cas d'exécution (délai {DELAI_S:.0f} s, plafond {PLAFOND_OCTETS} octets par flux)")
    r = executer_isole(CODE_BENIN)
    print(f"  bénin           → {r.verdict} ; code retour {r.code_retour} ; sortie : {r.sortie.strip()}")
    assert (r.verdict, r.code_retour, r.sortie.strip()) == ("ok", 0, "5558.32")
    executions = [r]
    r = executer_isole(CODE_BOUCLE)
    print(f"  boucle infinie  → {r.verdict} ; processus arrêté et attendu : {r.termine} ; octets gardés : {r.octets_gardes}")
    assert r.verdict == "délai dépassé" and r.termine and r.octets_gardes == 0
    executions.append(r)
    motifs = motifs_de_refus(CODE_IMPORT)
    print(f"  import interdit → refusé par la politique, jamais exécuté ({motifs[0]})")
    assert motifs == ["import non autorisé : socket"]
    r = executer_isole(CODE_SORTIE)
    que_des_x = set(r.sortie) == {"x"}
    print(f"  sortie énorme   → {r.verdict} ; {r.octets_gardes} octets gardés sur 2 000 000 prévus ; "
          f"tous des « x » : {que_des_x} ; arrêté avant la fin : {r.code_retour != 0}")
    assert r.verdict == "sortie tronquée" and r.octets_gardes == PLAFOND_OCTETS and que_des_x
    assert r.code_retour != 0 and r.termine        # arrêté au premier octet de trop, puis attendu
    executions.append(r)
    r = executer_isole(CODE_ERREUR)
    derniere = r.erreurs.strip().splitlines()[-1]
    print(f"  erreur          → {r.verdict} ; code retour {r.code_retour} ; {derniere}")
    assert r.verdict == "erreur" and r.code_retour == 1 and derniere == "ZeroDivisionError: division by zero"
    executions.append(r)
    assert all(e.termine and e.octets_gardes <= PLAFOND_OCTETS for e in executions)

    print("3. Contournement du filtre : la couche 1 cède, les couches suivantes tiennent")
    os.environ["CLE_API_DEMO"] = "valeur-factice"              # un secret du processus parent
    r = executer_isole(CODE_CONTOURNEMENT)
    for ligne in r.sortie.strip().splitlines():
        print(f"  {ligne}")
    assert r.verdict == "ok" and "module chargé : os" in r.sortie
    assert "clé du parent visible : False" in r.sortie and "dossier courant : ['programme.py']" in r.sortie
    assert os.environ["CLE_API_DEMO"] == "valeur-factice"      # le parent l'a, l'enfant ne l'a pas reçue

    print("4. L'outil dans la boucle d'agent : le refus repart vers le modèle, qui se corrige")
    script = [
        Reponse("tool_use", [appel_outil("executer_python", {"code": CODE_IMPORT}, "s1")]),
        Reponse("tool_use", [appel_outil("executer_python", {"code": CODE_BENIN}, "s2")]),
        Reponse("end_turn", [texte("La mensualité vaut 5 558,32 AED.")]),
    ]
    res = executer_agent(FakeLLM(script), "Analyste. Le code s'exécute dans une sandbox.",
                         "Mensualité de 1 M AED à 4,5 % sur 25 ans ?", {"executer_python": executer_python}, [])
    for _, _, sortie in res["trace"]:
        print(f"  executer_python -> {sortie}")
    print(f"  réponse : {res['reponse']}")
    assert res["statut"] == "fini" and res["etapes"] == 3
    assert res["trace"][0][2] == "ERREUR import non autorisé : socket"
    assert res["trace"][1][2] == {"verdict": "ok", "sortie": "5558.32", "erreur": ""}

    print("5. Défense en profondeur (εᵢ illustratifs : politique, processus, conteneur, micro-VM)")
    eps = [1.0, 0.1, 0.01, 0.001]
    p_ind = evasion_independante(eps)
    bas, haut = bornes_frechet(eps)
    print(f"  indépendance : {p_ind:.0e} ; sans la couche politique : {evasion_independante(eps[1:]):.0e}")
    print(f"  sans hypothèse d'indépendance : {bas:g} ≤ P ≤ {haut:g}")
    assert abs(p_ind - 1e-6) < 1e-18 and p_ind == evasion_independante(eps[1:])
    assert (bas, haut) == (0.0, 0.001)
    noyau = 0.005                                              # faille commune au processus et au conteneur
    assert bornes_frechet([0.1, 0.01])[1] >= noyau > 0.1 * 0.01
    print(f"  noyau partagé : P(processus et conteneur franchis) ≥ {noyau} au lieu de {0.1 * 0.01:g}")
    print("OK — toutes les vérifications sont passées.")


if __name__ == "__main__":
    main()
```

### Sortie attendue

```text
1. Politique sur le texte du code (liste blanche de modules, noms interdits)
  import math          → accepté
  import socket        → refusé (import non autorisé : socket)
  from os import path  → refusé (import non autorisé : os)
  eval('2 + 2')        → refusé (nom interdit : eval)
  if False: import os  → refusé (import non autorisé : os)
  contournement        → accepté
2. Quatre cas d'exécution (délai 2 s, plafond 4096 octets par flux)
  bénin           → ok ; code retour 0 ; sortie : 5558.32
  boucle infinie  → délai dépassé ; processus arrêté et attendu : True ; octets gardés : 0
  import interdit → refusé par la politique, jamais exécuté (import non autorisé : socket)
  sortie énorme   → sortie tronquée ; 4096 octets gardés sur 2 000 000 prévus ; tous des « x » : True ; arrêté avant la fin : True
  erreur          → erreur ; code retour 1 ; ZeroDivisionError: division by zero
3. Contournement du filtre : la couche 1 cède, les couches suivantes tiennent
  module chargé : os
  clé du parent visible : False
  dossier courant : ['programme.py']
4. L'outil dans la boucle d'agent : le refus repart vers le modèle, qui se corrige
  executer_python -> ERREUR import non autorisé : socket
  executer_python -> {'verdict': 'ok', 'sortie': '5558.32', 'erreur': ''}
  réponse : La mensualité vaut 5 558,32 AED.
5. Défense en profondeur (εᵢ illustratifs : politique, processus, conteneur, micro-VM)
  indépendance : 1e-06 ; sans la couche politique : 1e-06
  sans hypothèse d'indépendance : 0 ≤ P ≤ 0.001
  noyau partagé : P(processus et conteneur franchis) ≥ 0.005 au lieu de 0.001
OK — toutes les vérifications sont passées.
```

Ce que le programme montre : l'isolement ne vient pas de ce qu'on interdit dans le texte du code, mais de ce qu'on retire au processus qui l'exécute — ses variables, ses fichiers, son temps, sa sortie. Le filtre de texte sert le message ; les couches servent la sécurité.

## Squelette algorithmique

Le fichier contient deux algorithmes principaux : exécuter un code dans un sous-processus isolé et borné, et lire un flux sans jamais dépasser un plafond de mémoire. Dans les complexités, L désigne la longueur du code, N le nombre d'octets qu'un flux produit et B le plafond par flux.

### Exécuter un code isolé

Entrées : un code, un délai, un plafond. Sortie : un verdict, un code retour, la sortie et les erreurs plafonnées. Idée : retirer au processus ses droits, puis l'arrêter sans pitié s'il dépasse le temps ou la sortie permise.

```text
ALGORITHME ExécuterIsolé
ENTRÉES : code c ; délai t_max ; plafond B ; mémoire M
SORTIE  : (verdict, code_retour, sortie, erreurs, octets_gardés, terminé)
  créer un dossier temporaire jetable d
  écrire c dans d/programme.py
  env ← {}                                  ▷ aucune variable du parent (hors SYSTEMROOT sous Windows)
  lancer P ← interpréteur isolé (-I) sur d/programme.py, cwd = d, entrée vide,
         sorties en tubes, nouveau groupe de processus
         (POSIX : poser les limites mémoire et CPU avant exec)
  démarrer un LecteurBorné sur chaque tube, plafond B, « au trop-plein : tuer P »
  délai_dépassé ← FAUX
  ESSAYER attendre P au plus t_max secondes
  SI le délai expire ALORS
    délai_dépassé ← VRAI ; Tuer(P) ; attendre P au plus t_arrêt
  FIN SI
  joindre les deux lecteurs (au plus t_join chacun) ; fermer les tubes
  terminé ← (P est bien terminé)
  détruire d
  verdict ← Classer(délai_dépassé, un flux tronqué ?, code retour de P)
  RETOURNER (verdict, …)

ALGORITHME Tuer(P)                           ▷ n'exécute aucun code du programme
  SI P déjà terminé ALORS RETOURNER FIN SI
  POSIX : envoyer SIGKILL au groupe de P ; Windows : TerminateProcess(P)
```

**Complexité :** O(L) pour écrire le code, puis le coût propre du programme, borné par t_max en temps réel. La mémoire du parent est O(B) par flux, indépendante de N (point 1), au lieu de O(N) pour une lecture non bornée. L'attente totale est bornée par t_max + t_arrêt + 2 t_join (point 2).

**Du squelette au code :** `ExécuterIsolé` est `executer_isole`, avec `tempfile.TemporaryDirectory`, `subprocess.Popen([... "-I" ...])`, les deux `LecteurBorne`, `proc.wait(timeout=...)` puis `tuer` ; `Tuer` est `tuer(proc)` ; `Classer` est `classer`.

### Lire un flux sans dépasser un plafond

Entrée : un flux, un plafond B, une action de trop-plein. Sortie : au plus B octets gardés, et un drapeau. Idée : ne jamais stocker plus que B, et arrêter le producteur dès qu'il déborde.

```text
ALGORITHME LecteurBorné
ENTRÉES : flux f ; plafond B ; action trop_plein
SORTIE  : gardés (≤ B octets), tronqué (booléen)
  gardés ← octets vides ; tronqué ← FAUX
  TANT QUE lire un bloc b sur f ne renvoie pas « fin de flux » FAIRE
    place ← max(0, B − longueur(gardés))
    gardés ← gardés + les `place` premiers octets de b
    SI longueur(b) > place ET NON tronqué ALORS
      tronqué ← VRAI ; trop_plein()          ▷ arrêter le producteur
    FIN SI
  FIN TANT QUE
  RETOURNER (gardés, tronqué)
```

**Complexité :** O(min(N, B) + k) en mémoire, où k est la taille d'un bloc de lecture (65 536 octets), parce que le code ajoute au plus B octets et jette le reste ; O(N) en temps au pire, mais l'arrêt du producteur ramène en pratique la lecture à peu après B octets. L'invariant longueur(gardés) ≤ B tient à chaque tour (point 1).

**Du squelette au code :** c'est `LecteurBorne._boucle`, avec `read1(65536)`, `place = max(0, self.plafond - len(self.gardes))`, et `self.trop_plein()` qui vaut `lambda: tuer(proc)`.

## Cas d'usage réels aux Émirats

Les délais, plafonds et seuils ci-dessous sont illustratifs ; on les règle sur l'usage réel de chaque service, et les couches réseau et appels système s'ajoutent en production.

### Banque — un calcul sur un relevé déposé par le client

Une banque de détail de Dubaï laisse son assistant additionner et vérifier les lignes d'un relevé qu'un client dépose, en écrivant un petit programme Python plutôt qu'en calculant de tête, ce qui réduit les erreurs. Le relevé est un texte non fiable, et le code que le modèle en tire l'est tout autant. L'agent l'exécute avec `executer_python` : délai de 2 s, sortie plafonnée à 4 096 octets, environnement vide, dossier jetable, si bien qu'aucune clé d'accès au cœur bancaire ni aucun fichier d'un autre client n'est à portée du code. Un relevé piégé qui ferait écrire `import socket` est refusé par la politique avant toute exécution, et le refus, lisible, repart vers le modèle qui se corrige (section 4). Sans sandbox, exécuter ce code serait une action irréversible que le score de risque de l'étape 67 devrait bloquer d'office ; avec elle, l'action redevient quasi une lecture. On suit le taux d'exécutions refusées par la politique et le taux de dépassements de délai, dont une hausse signale un abus ou un code mal formé.

### Assurance — agréger un fichier de sinistres sans le laisser fuir

Un assureur auto et santé, supervisé par la CBUAE, fait calculer par son agent des statistiques sur un export de sinistres : montant moyen par garage, nombre de dossiers rouverts, vétusté médiane. Le fichier contient des données de santé, la classe la plus sensible du score de risque (étape 67). Le code généré tourne dans la sandbox, dont le dossier jetable ne contient que `programme.py` : le code ne peut pas lire d'autre fichier du poste, et son environnement vide le prive de tout identifiant qui lui permettrait d'envoyer les données ailleurs — l'absence de réseau dans un vrai déploiement ferme la dernière porte. La sortie plafonnée empêche aussi qu'un programme recopie tout le fichier dans le contexte du modèle, où il serait journalisé. Sans ce confinement, un agent qui exécute du code sur des données de santé serait une fuite en attente. On suit le nombre d'octets moyen renvoyé par exécution et le nombre d'exécutions tronquées.

### BTP — un métré calculé sur le poste du chantier

Un groupe de construction qui mène de grands chantiers à Dubaï installe sur le poste de ses métreurs un agent qui calcule des quantités à partir des devis : surfaces, volumes de béton, TVA de 5 % sur une facture de 120 000 AED HT, soit 6 000 AED. L'agent écrit un programme et l'exécute dans la sandbox, lancée en sous-processus isolé avec l'option `-I` pour qu'aucun fichier déposé à côté ne se fasse passer pour un module standard. Le délai de 2 s protège le poste d'une boucle infinie qui le figerait pendant que le métreur attend, et l'arrêt par `TerminateProcess` est non interceptable, donc fiable même si le programme a installé un gestionnaire d'interruption. Sans délai, une erreur de génération suffirait à bloquer l'outil de travail. On suit le temps d'exécution médian et le nombre de dépassements de délai par jour.

### Secteur public — du code fourni par l'usager, borné en ressources

Une entité de services publics en ligne, accessible par UAE Pass, propose un petit bac à calcul où l'usager, ou l'assistant pour lui, soumet une formule à évaluer, par exemple pour simuler des frais. Ce code vient de l'extérieur : il faut le traiter comme hostile. La sandbox le confine dans un sous-processus isolé, avec des limites de mémoire et de temps CPU posées sous POSIX par `setrlimit`, de sorte qu'un programme glouton ne prive pas les autres usagers de la machine. La sortie plafonnée garde le service réactif. Le principe de minimisation de la PDPL est respecté : l'environnement vide ne transmet aucune donnée de session au code soumis, qui ne voit que ce qu'on lui passe explicitement. Sans bornes de ressources, un seul usager pourrait épuiser la machine, volontairement ou non. On suit la mémoire et le temps CPU consommés par exécution, et le taux d'exécutions arrêtées pour dépassement.

### RH — un script de paie jetable, sans accès au système officiel

Un cabinet RH multi-émirats laisse son agent préparer des calculs de paie : indemnité de fin de service, prorata d'un mois incomplet, retenues. Le code tourne dans la sandbox et n'a **aucun** accès au système de paie ni au système WPS : il reçoit les nombres en entrée et rend un résultat, que le gestionnaire relit. Cette séparation est volontaire : le calcul est jetable et vérifiable, l'écriture réelle dans le système officiel reste un outil distinct, à effet de bord, soumis à l'approbation humaine de l'étape 66. Ainsi, même un code généré à partir d'un document piégé ne peut rien déclencher d'irréversible : au pire, il rend un mauvais nombre, que la relecture attrape. Sans cette frontière, un agent qui exécute du code et écrit dans la paie cumulerait deux pouvoirs qui ne doivent jamais se rencontrer. On suit la part des calculs modifiés par le gestionnaire après relecture.

### Crypto — un filtre qui informe, des couches qui protègent

Une plateforme d'actifs virtuels agréée par la VARA laisse son agent de surveillance calculer des indicateurs sur les carnets d'ordres. L'équipe sait que son filtre d'`import` se contourne : elle l'a vérifié elle-même, comme la section 3 du programme, et ne compte donc jamais dessus comme sur une barrière. Le filtre sert à donner au modèle un message clair quand il tente un module non prévu ; la sécurité, elle, vient du processus isolé, de l'environnement vide et, en production, d'un conteneur avec filtrage des appels système. L'équipe choisit des couches de natures différentes, car une faille commune ferait tomber ensemble des couches semblables, et la borne de Fréchet rappelle que le montage ne vaut jamais mieux que sa meilleure couche (démonstration, point 5). Sans cette lucidité, on croirait protégé un agent qui ne l'est pas. On suit le taux de refus du filtre et, séparément, tout événement d'évasion détecté par la couche conteneur.

## Pièges et limites

- **Prendre un filtre de texte pour une frontière.** L'analyse des `import` ou des noms se contourne (point 3) et refuse du code sain. Elle informe le modèle ; elle ne protège pas. La protection vient du processus isolé.
- **Croire qu'un seul processus suffit.** Un sous-processus partage le noyau de la machine. Pour du code vraiment hostile, on ajoute un conteneur (seccomp, quotas, pas de réseau) ou une micro-VM. Le code de ce fichier est la première couche, pas la dernière.
- **Oublier de couper le réseau.** La bibliothèque standard ne le fait pas de façon portable ; un code isolé mais connecté peut exfiltrer. On ferme le réseau au niveau du conteneur.
- **Lire la sortie sans plafond.** `communicate()` garde tout en mémoire : un programme bavard remplit la RAM du parent et le contexte du modèle. On plafonne et on arrête le producteur.
- **Utiliser une interruption interceptable pour le délai.** Un `SIGTERM` ou un `KeyboardInterrupt` peut être attrapé et ignoré. Seuls `SIGKILL` et `TerminateProcess` garantissent l'arrêt.

### Exercice feuille blanche

1. Sans regarder le code, écrire `LecteurBorne._boucle` et prouver l'invariant longueur(gardés) ≤ B. Puis écrire `classer` et vérifier qu'un délai dépassé l'emporte sur un code retour non nul.
2. Prédire, puis vérifier : on fixe `plafond_octets=10` et l'on exécute `print('x' * 100)`. Quel verdict, combien d'octets gardés ? (Réponse : « sortie tronquée », 10 octets.)
3. Trouver le bug : une variante de `tuer` utilise `os.kill(proc.pid, signal.SIGTERM)` au lieu de `SIGKILL`. Que se passe-t-il si le code sandboxé installe un gestionnaire de `SIGTERM` qui l'ignore ? (Réponse : il survit à l'ordre, `proc.wait` finit par expirer de nouveau, et l'agent attend plus longtemps ; la borne de temps n'est plus garantie.)
4. Calculer : trois couches aux εᵢ = 0,2, 0,05 et 0,01. Donner le produit sous indépendance et les deux bornes de Fréchet. (Réponse : 0,0001 ; borne basse max(0 ; 0,26 − 2) = 0 ; borne haute min = 0,01.)

## Pour aller plus loin

En production, l'exécution de code non fiable s'appuie sur un conteneur durci (filtrage seccomp des appels système, système de fichiers en lecture seule, pas de réseau, utilisateur sans privilèges) ou sur une micro-VM à noyau séparé, qui coupe le lien avec le noyau de l'hôte. Les limites de ressources, ici posées par `setrlimit` sous POSIX, se règlent plutôt par les quotas du conteneur (cgroups), portables et plus complets. Enfin, certaines offres exécutent le code dans un environnement géré côté serveur, à l'écart de l'agent : le principe reste celui de ce fichier, seules les couches changent.

> Suite : [Notation de Kendall](<../12-Production-Couts-Optimisation/68-Notation-de-Kendall.md>) — étape 68.
