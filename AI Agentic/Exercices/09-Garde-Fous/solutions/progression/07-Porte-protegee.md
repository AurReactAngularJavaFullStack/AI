# Étape 7 — La porte protégée

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 6 — L'approbation humaine](<06-Approbation-humaine.md>) · Suivant : [Étape 8 — L'outil de virement](<08-Outil-de-virement.md>)

## Comment raisonner

La politique existe (étape 1), le journal aussi (étape 3). Il reste à **brancher** la politique sur chaque appel d'outil, sans modifier le module `outils` du palier 04 : aucun palier ne réécrit un module antérieur, on compose. Le palier 04 fournit déjà, pour chaque outil, une porte `registre.porte(nom)` qui valide les arguments puis exécute la fonction. On va l'**envelopper** : une nouvelle fonction, du même nom, qui vérifie la politique, journalise la décision, puis délègue à la porte. L'ordre de l'étape 77 est conservé : politique, puis schéma, puis outil.

Pour un développeur Spring, c'est exactement un intercepteur, ou un aspect `@Around` : du code qui s'exécute autour de la méthode du service, avec un contexte de sécurité, et qui peut empêcher la méthode d'être atteinte.

Deux questions guident l'écriture. **Quand lit-on la session ?** À chaque appel, parce que le rôle peut changer entre la construction des outils et leur utilisation (une session qui expire, un test qui change de rôle). **Comment chaque enveloppe connaît-elle son outil ?** C'est le piège de cette étape.

## Un brouillon, deux bugs

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proteger(registre, session, journal, politique)`** — Ce brouillon ressemble à un chef de la sécurité qui photocopie la liste des droits le matin et la distribue à tous ses vigiles, sans jamais la mettre à jour, puis leur donne à tous la même consigne écrite sur le même bout de papier. Il reçoit le registre, la session, le journal et une politique facultative, copie une fois pour toutes le rôle et les portées de la session, puis parcourt les noms d'outils du registre et range sous chacun une fonction `appeler` définie dans la boucle. Il rend ce dictionnaire nom → fonction, mais n'utilise jamais le journal, et toutes ses fonctions partagent la même variable `nom`, qui vaut le dernier outil parcouru une fois la boucle terminée.

**`appeler(arguments)`** — Cette fonction interne, définie dans la boucle de `proteger`, devrait être le vigile posté devant une porte précise ; elle reçoit les arguments nommés de l'appel, demande à `autoriser` si le rôle copié à la construction peut appeler l'outil `nom`, lève `RefusPolitique(motif)` en cas de refus, et sinon rend le résultat de `registre.porte(nom)` appliqué aux arguments. Le malheur est que `nom` est lu au moment de l'appel, pas au moment de la définition : pour un registre des cinq outils métier, chaque vigile contrôle et ouvre la porte de `"tva"`, avec les droits d'une session qui a peut-être changé depuis, et sans laisser la moindre trace au journal.

```python
# [extrait] brouillon
def proteger(registre, session, journal, politique=None):
    role, portees = session["role"], session["portees"]          # erreur 1 : lu une seule fois
    outils = {}
    for nom in registre.outils:
        def appeler(**arguments):
            ok, motif = autoriser(role, nom, portees, politique)  # erreur 2 : « nom » vaut le dernier outil
            if not ok:
                raise RefusPolitique(motif)
            return registre.porte(nom)(**arguments)
        outils[nom] = appeler
    return outils
```

**Erreur 1.** Le rôle et les portées sont copiés à la construction. Si la session passe ensuite au rôle `assistant_public`, les outils continuent d'appliquer les droits de `client_banque`. Le test `test_politique_avant_le_schema` fait exactement ce changement, et attend un refus.

**Erreur 2, la plus sournoise.** Une fonction Python définie dans une boucle capture la **variable** `nom`, pas sa valeur au moment de la définition. Quand on appelle `outils["mensualite"]` après la boucle, `nom` vaut la dernière valeur prise par la boucle, `"tva"` pour un registre qui ne contient que les cinq outils métier : la politique est vérifiée pour la TVA, et c'est la porte de la TVA qui est appelée avec les arguments d'une mensualité. En Java, ce bug est impossible : une lambda ne peut capturer qu'une variable effectivement finale, et le compilateur refuserait ce code.

Enfin, ce brouillon ne journalise rien : un refus ne laisserait aucune trace pour l'audit.

## La solution : une fonction fabrique

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`proteger(registre, session, journal, politique)`** — Cette fois, le chef de la sécurité recrute un vigile distinct pour chaque porte et lui remet une consigne à son nom. La fonction reçoit le registre du palier 04, la session partagée avec l'appelant, le journal d'audit et une politique facultative ; elle ne modifie rien de ces objets et se contente d'appeler la fabrique `enveloppe` une fois par nom d'outil du registre. Elle rend le dictionnaire nom → appelable qui remplacera `registre.appelables()` dans `executer_agent`, de sorte que chaque appel d'outil traverse désormais la politique avant le schéma.

**`enveloppe(nom)`** — Cette fonction interne, qui vit dans `proteger`, est le bureau d'embauche qui remet à chaque vigile son badge personnel. Elle reçoit le nom d'un outil, demande une seule fois au registre sa porte `registre.porte(nom)`, qui valide le schéma puis exécute l'outil, et rend une fonction `appeler` toute neuve qui garde pour toujours ce `nom` et cette porte-là. Chaque appel à `enveloppe` crée sa propre portée locale : c'est ce qui corrige le piège du brouillon, où toutes les fonctions de la boucle partageaient le dernier nom parcouru.

**`appeler(arguments)`** — Cette fonction interne, fabriquée par `enveloppe` à l'intérieur de `proteger`, est le vigile lui-même, en faction devant une seule porte. Elle reçoit les arguments nommés extraits du bloc `tool_use`, relit à cet instant précis le rôle et les portées de la session, consulte `autoriser`, puis journalise « politique … -> … : … » que la réponse soit un accord ou un refus. En cas de refus, elle lève `RefusPolitique(motif)` sans même toucher la porte, si bien que des arguments invalides sous le rôle `assistant_public` ne déclenchent aucun message du validateur ; sinon, elle rend le résultat de la porte, par exemple `{'mensualite_aed': 5558.32}` une fois la session repassée au rôle `client_banque`.

```python
# [extrait] agent/garde_fous.py
def proteger(registre: Registre, session: dict, journal: JournalAudit, politique: dict | None = None) -> dict:
    ...
    def enveloppe(nom: str):
        porte = registre.porte(nom)

        def appeler(**arguments):
            ok, motif = autoriser(session["role"], nom, session["portees"], politique)
            journal.journaliser(f"politique {session['role']} -> {nom} : {motif}")
            if not ok:
                raise RefusPolitique(motif)
            return porte(**arguments)
        return appeler
    return {nom: enveloppe(nom) for nom in registre.outils}
```

**Ligne par ligne.**

- `enveloppe(nom)` est une **fonction fabrique** : chaque appel crée une nouvelle portée locale, avec **son propre** `nom`. La fonction `appeler` qu'elle rend capture ce `nom`-là, qui ne changera plus. C'est la correction standard de l'erreur 2.
- `porte = registre.porte(nom)` est calculé une fois par outil, à la construction : la porte du palier 04 ne dépend pas de la session, inutile de la refabriquer à chaque appel.
- `appeler(**arguments)` reçoit les arguments nommés que la boucle extrait du bloc `tool_use` (`outils[bloc.name](**bloc.input)` au palier 04).
- `session["role"]` et `session["portees"]` sont lus **dans** `appeler`, donc à chaque appel : c'est la correction de l'erreur 1. La session est un dictionnaire partagé avec l'appelant, rempli par l'authentification ; le modèle n'a aucun moyen d'y écrire.
- La décision est journalisée **avant** de lever, que ce soit un accord ou un refus : l'audit voit les deux.
- Un refus lève `RefusPolitique` (définie au palier 04, sous-classe de `PermissionError`) : la porte n'est même pas appelée, donc le schéma n'est pas consulté et l'outil n'est pas atteint.
- La compréhension finale construit le dictionnaire nom → enveloppe, à passer à `executer_agent` à la place de `registre.appelables()`.

**Analogie Java.** `proteger` construit des proxys, comme Spring AOP : `appeler` joue le rôle de la méthode `invoke` d'un `MethodInterceptor`, `autoriser` celui d'un `@PreAuthorize`, et `session` celui du `SecurityContextHolder`, relu à chaque invocation. `porte(**arguments)` est l'appel à `invocation.proceed()`.

**Pourquoi la politique avant le schéma ?** Un rôle qui n'a pas le droit d'appeler un outil n'a pas non plus à apprendre, par les messages du validateur, quels arguments cet outil attend. Et le coût d'un refus de politique est minimal : un accès à un dictionnaire, sans parcourir le schéma.

## Une vérification à la console

Le test de cette étape construit un monde complet qui a aussi besoin de l'outil de virement (étape 8). En attendant, on peut vérifier l'enveloppe à la main avec les seuls outils métier, depuis `projet/` :

```text
>>> from agent.garde_fous import JournalAudit, proteger
>>> from agent.outils import Registre, enregistrer_outils_metier
>>> session = {"role": "assistant_public", "portees": {"lecture"}}
>>> j = JournalAudit()
>>> outils = proteger(enregistrer_outils_metier(Registre()), session, j)
>>> outils["mensualite"](principal="pas un nombre", taux_annuel=0.045, n_mois=300)
Traceback (most recent call last):
  ...
agent.outils.RefusPolitique: outil mensualite non autorisé pour le rôle assistant_public
>>> session.update(role="client_banque")
>>> outils["mensualite"](principal=1_000_000, taux_annuel=0.045, n_mois=300)
{'mensualite_aed': 5558.32}
>>> j.textes()
['politique assistant_public -> mensualite : outil mensualite non autorisé pour le rôle assistant_public', 'politique client_banque -> mensualite : autorisé']
```

Le premier appel a des arguments invalides, mais c'est la politique qui répond. Le même objet `outils`, après le changement de rôle, laisse passer : la session est bien relue à chaque appel.

## Les tests qui passeront à l'étape suivante

```text
python -m unittest -v tests.test_09_garde_fous.TestPorteProtegeeEtVirement.test_politique_avant_le_schema
```

Ce test appelle `monde()`, qui enregistre aussi l'outil de virement avant d'appeler `proteger` : tant que `enregistrer_virement` lève `NotImplementedError`, il échoue. Il passera dès l'étape 8, et vérifiera alors ce que montre la console : `RefusPolitique`, et une seule ligne de journal.
