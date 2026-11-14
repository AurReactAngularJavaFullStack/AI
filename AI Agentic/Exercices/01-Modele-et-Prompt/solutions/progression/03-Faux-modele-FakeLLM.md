# Étape 3 — Le faux modèle

> Palier 01, étape 3 sur 7 · Précédent : [Étape 2 — Blocs et réponses](<02-Blocs-et-reponses.md>) · Suivant : [Étape 4 — La softmax](<04-Softmax.md>) · [Retour à l'énoncé](<../../README.md>)

**Objectif de l'étape :** écrire `FakeLLM`, l'adaptateur de test du port LLM. Les trois tests de `TestPortLLM` passent à la fin.

## Comment raisonner

Le port LLM n'a qu'une méthode : `create(system=…, messages=…, tools=…)`, qui rend une `Reponse`. Le vrai adaptateur (palier 12) l'implémente en appelant l'API ; il coûte de l'argent, demande une clé, dépend du réseau et ne répond jamais deux fois pareil. Pour tester la boucle, les outils et les garde-fous, il faut l'inverse : un modèle **scripté**, à qui l'on dicte à l'avance ses réponses, dans l'ordre.

On liste ce que les tests vont exiger, avant d'écrire une ligne :

1. **la même signature** que le vrai adaptateur, arguments nommés compris : la boucle ne doit pas savoir lequel elle utilise ;
2. **rejouer** les réponses du script dans l'ordre, une par appel ;
3. **compter** les appels (`appels`), pour vérifier qu'une boucle s'arrête au bon moment ;
4. **garder une trace** de chaque requête (`requetes`), pour vérifier ce que la boucle a envoyé ;
5. **échouer bruyamment** quand le script est épuisé : un scénario qui appelle le modèle une fois de trop est un scénario faux, et il doit se voir.

Chaque exigence donne une ou deux lignes de code. La difficulté n'est pas la quantité, c'est l'ordre des lignes et une copie qu'on oublie facilement.

## Un brouillon qui a l'air juste

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`FakeLLM.__init__(script)`** — Dans ce brouillon, le constructeur ressemble à un comédien distrait qui, au lieu d'apprendre son texte, se contente de lire par-dessus l'épaule du metteur en scène : il reçoit la liste des réponses prévues et la range telle quelle dans `script`, sans copie, si bien que toute modification faite ensuite par l'appelant change la pièce en cours de route. Il met aussi le compteur `appels` à 0 et ouvre un registre `requetes` vide, ce qui, en soi, est correct ; c'est le partage de la liste qui constitue le troisième défaut décrit plus bas.

**`FakeLLM.create(system, messages, tools)`** — La méthode du brouillon reçoit, en arguments nommés, le système, les messages et les outils, note aussitôt dans `requetes` un dictionnaire qui pointe vers ces listes mêmes plutôt que vers des copies, lit la réponse d'indice `appels`, incrémente le compteur et renvoie cette réponse. Elle rejoue bien le script dans l'ordre, mais la requête gardée grandit quand la boucle allonge sa liste de messages, au point d'en montrer deux là où le modèle n'en avait reçu qu'un, et un appel de trop lève un `IndexError` muet au lieu de la `RuntimeError` qu'attend le test.

```python
# [extrait] brouillon
class FakeLLM:
    def __init__(self, script: list) -> None:
        self.script = script                    # même liste que l'appelant
        self.appels = 0
        self.requetes = []

    def create(self, *, system: str, messages: list, tools: list):
        self.requetes.append({"system": system, "messages": messages, "tools": tools})   # pas de copie
        reponse = self.script[self.appels]      # IndexError quand le script est épuisé
        self.appels += 1
        return reponse
```

Ce brouillon rejoue bien les réponses dans l'ordre. Il a pourtant trois défauts, et les tests en attrapent deux.

**Défaut 1 : la requête gardée change après coup.** La boucle d'agent garde **une seule** liste `messages` pendant toute la conversation et lui ajoute un message à chaque tour. Le brouillon range dans `requetes` une référence vers cette liste, pas son contenu. Au tour suivant, la requête « gardée » a grandi :

```text
# [extrait] console
>>> llm = FakeLLM([r1, r2])                     # version brouillon
>>> messages = [{"role": "user", "content": "q"}]
>>> r = llm.create(system="s", messages=messages, tools=[])
>>> messages.append({"role": "assistant", "content": r.content})
>>> len(llm.requetes[0]["messages"])
2
```

Au moment du premier appel, le modèle n'avait reçu qu'un message ; la trace en montre deux. Un test qui vérifie « au premier appel, le modèle n'avait que la question » se tromperait. C'est exactement ce que contrôle `test_fake_rejoue_dans_l_ordre_et_garde_les_requetes`. Le même piège existe en Java avec l'`ArgumentCaptor` de Mockito, qui capture la référence d'une liste, pas une copie.

**Défaut 2 : l'erreur de fin de script est muette.** Quand le script est épuisé, `self.script[self.appels]` lève `IndexError: list index out of range`. Le message ne dit pas ce qui se passe, et `IndexError` n'est pas l'exception attendue par `test_script_epuise`, qui veut une `RuntimeError`.

**Défaut 3 : `self.script = script` partage la liste de l'appelant.** Si le test modifie sa liste après avoir créé le faux modèle, le script change sous les pieds du modèle. Aucun test ne l'attrape, mais c'est la même famille de bug que le défaut 1.

## La version correcte

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`FakeLLM.__init__(script)`** — Le constructeur corrigé est celui d'un comédien consciencieux qui recopie son rôle dans son propre carnet : il reçoit la liste des réponses prévues et en garde une nouvelle liste, `list(script)`, pour que l'appelant puisse modifier la sienne sans effet sur la pièce. Il met ensuite le compteur `appels` à 0, compteur qui sert aussi d'indice de la prochaine réplique, et crée dans le constructeur même un registre `requetes` vide, propre à chaque faux modèle, où chaque appel laissera sa trace pour les tests.

**`FakeLLM.create(system, messages, tools)`** — La méthode corrigée suit un ordre de guichetier rigoureux, vérifier, enregistrer, rendre : elle reçoit en arguments nommés obligatoires le système, les messages et les outils, lève d'abord `RuntimeError` (« script épuisé : le faux LLM n'a plus de réponse prévue ») si `appels` a atteint la longueur du script, sans rien noter. Sinon elle range dans `requetes` le système et des copies superficielles des messages et des outils, figées telles qu'au moment de l'appel, lit la réponse d'indice courant, incrémente `appels` et la renvoie. Avec un script de deux réponses, le troisième appel est refusé, et l'égalité entre le nombre de requêtes et `appels` reste toujours vraie.

```python
# [extrait] agent/modele.py
class FakeLLM:
    ...
    def __init__(self, script: list) -> None:
        self.script = list(script)
        self.appels = 0
        self.requetes: list[dict] = []

    def create(self, *, system: str, messages: list, tools: list) -> Reponse:
        """Même signature que l'adaptateur Claude ; rend la réponse suivante du script."""
        if self.appels >= len(self.script):
            raise RuntimeError("script épuisé : le faux LLM n'a plus de réponse prévue")
        self.requetes.append({"system": system, "messages": list(messages), "tools": list(tools)})
        reponse = self.script[self.appels]
        self.appels += 1
        return reponse
```

La ligne `...` remplace la docstring de la classe, déjà présente dans le squelette.

**Le constructeur.**

- `self.script = list(script)` : `list(...)` crée une **nouvelle** liste avec les mêmes éléments. Le faux modèle a désormais son propre script ; l'appelant peut modifier le sien sans effet. C'est une copie défensive, comme `List.copyOf(script)` dans un constructeur Java.
- `self.appels = 0` : le compteur d'appels, qui sert aussi d'indice de la prochaine réponse.
- `self.requetes: list[dict] = []` : l'annotation dit au lecteur que la liste contiendra des dictionnaires. Une liste vide créée **dans** le constructeur est propre à chaque objet : pas de partage, contrairement au piège de l'étape 2.

**La signature de `create`.** L'étoile seule, `*`, rend tous les paramètres qui la suivent **nommés obligatoirement** : `llm.create(system="s", messages=m, tools=[])` marche, `llm.create("s", m, [])` lève `TypeError`. Pourquoi l'imposer ? Parce que le SDK Anthropic n'accepte que des arguments nommés : si la boucle appelait le faux modèle par position, elle casserait le jour où on lui donne le vrai. Java n'a pas d'arguments nommés ; l'équivalent le plus proche serait un objet de paramètres construit par un builder.

**L'ordre des trois blocs de `create`, ligne par ligne.**

1. `if self.appels >= len(self.script): raise RuntimeError(...)` vient **en premier**. Après deux appels sur un script de deux réponses, `appels` vaut 2 et `len(self.script)` vaut 2 : le troisième appel est refusé avec un message qui dit exactement ce qui s'est passé. Parce que la vérification précède l'enregistrement, un appel refusé ne laisse aucune trace dans `requetes`, et l'on a toujours `len(requetes) == appels`.
2. `self.requetes.append({...})` enregistre la requête avec deux copies, `list(messages)` et `list(tools)`. La copie fige la liste **telle qu'elle était au moment de l'appel**. C'est une copie superficielle : les dictionnaires des messages sont partagés. Cela suffit, parce que la boucle ne modifie jamais un message déjà envoyé, elle en ajoute de nouveaux. Une copie profonde (`copy.deepcopy`) serait plus sûre mais plus lente, sans rien attraper de plus ici.
3. `reponse = self.script[self.appels]`, puis `self.appels += 1`, puis `return reponse` : on lit la réponse à l'indice courant **avant** d'incrémenter. Avec `appels` à 0, on rend `script[0]` et le compteur passe à 1.

**Le piège classique.** Incrémenter avant de lire (`self.appels += 1` puis `self.script[self.appels]`) : la première réponse est sautée, et la dernière lève l'erreur de fin de script un appel trop tôt. Le test `test_fake_rejoue_dans_l_ordre_et_garde_les_requetes` le voit, puisqu'il vérifie avec `assertIs` que le premier appel rend **le même objet** `r1`.

**Pourquoi le faux modèle ne regarde pas ce qu'on lui envoie.** Il rend sa réponse prévue quel que soit le prompt. C'est voulu : il prouve que la plomberie traite correctement chaque réponse possible, pas que le modèle prendrait la bonne décision. La qualité des décisions se mesure avec le vrai modèle, au palier 10.

## Les tests qui passent maintenant

```powershell
python -m unittest -v tests.test_01_modele.TestPortLLM
```

Les trois tests sont verts.

- `test_blocs`, déjà vert à l'étape 2.
- `test_fake_rejoue_dans_l_ordre_et_garde_les_requetes` : le script contient r1 (un appel d'outil) et r2 (une fin de tour). Le premier appel reçoit une liste d'un message et rend r1 ; le test ajoute la réponse à **la même liste** et rappelle avec un outil déclaré ; il reçoit r2. On vérifie ensuite `appels == 2`, une requête d'un message puis une de deux messages, et les outils du second appel.
- `test_script_epuise` : un script d'une réponse, un appel qui réussit, un second qui lève `RuntimeError`.

Pour n'en lancer qu'un : `python -m unittest -v tests.test_01_modele.TestPortLLM.test_script_epuise`.

## Ce qu'il faut retenir

- Le faux modèle a **la même signature** que le vrai, arguments nommés compris : c'est ce qui rend les deux adaptateurs interchangeables.
- On copie une liste qu'on garde et que l'appelant continue de modifier : `list(...)`.
- Vérifier, puis enregistrer, puis rendre : un appel refusé ne laisse pas de trace, et le message d'erreur dit ce qui s'est passé.

> Suivant : [Étape 4 — La softmax](<04-Softmax.md>)
