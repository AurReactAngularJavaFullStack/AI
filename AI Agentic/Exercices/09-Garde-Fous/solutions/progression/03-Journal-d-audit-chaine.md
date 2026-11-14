# Étape 3 — Le journal d'audit chaîné

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 2 — Masquer les données personnelles](<02-Masquer-les-donnees-personnelles.md>) · Suivant : [Étape 4 — Gravité et score de risque](<04-Gravite-et-score-de-risque.md>)

## Comment raisonner

Un journal d'audit répond à la question d'un auditeur : « qu'a décidé l'agent, quand, et pourquoi ? ». Deux exigences en découlent. Le journal ne doit **jamais** contenir de donnée personnelle en clair : on masque donc avant d'écrire, dans la méthode d'écriture elle-même, pour qu'aucun appelant ne puisse l'oublier. Et une modification après coup doit **se voir** : on chaîne les entrées, chaque empreinte dépendant de la précédente.

On écrit d'abord la forme d'une entrée, puisque l'écriture et la vérification doivent la calculer exactement de la même façon : un dictionnaire `{"t", "texte", "precedent", "hash"}`, et un **corps** haché qui ne dépend que de `t` et `texte`. On écrit ensuite `journaliser`, puis `verifier`, qui refait le calcul de `journaliser` entrée par entrée.

## La genèse, l'état et le corps haché

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`JournalAudit.__init__(horloge)`** — Le constructeur ressemble au greffier qui, le matin, pose sur son bureau un registre vierge et règle la pendule de la salle d'audience. Il reçoit une horloge simulée, celle que l'approbateur fera avancer plus tard, ou `None`, auquel cas il en crée une neuve qui démarre à 0 s ; il la range dans `self.horloge` et prépare la liste vide `self.entrees`. Il ne rend rien et n'écrit aucune ligne : il fixe seulement le temps de référence et le carnet public que les tests liront, et que la démonstration falsifiera exprès pour montrer que la retouche se voit.

**`JournalAudit.corps(t, texte)`** — Cette méthode statique est le formulaire préimprimé du greffier, toujours rempli dans le même ordre, de sorte que deux copies d'un même acte soient identiques au caractère près. Elle reçoit l'instant `t` et le texte déjà masqué, ne lit aucun attribut de l'objet, et rend `json.dumps` du dictionnaire `{"t": t, "texte": texte}` avec les clés triées et les accents gardés lisibles grâce à `ensure_ascii=False`. Pour l'exemple de l'énoncé, elle rend `{"t": 5.0, "texte": "virement vers [IBAN ••••3456]"}` ; c'est le texte canonique que l'écriture hachera et que la vérification recalculera à l'identique.

```python
# [extrait] agent/garde_fous.py
GENESE = "0" * 64


class JournalAudit:
    ...
    def __init__(self, horloge: Horloge | None = None) -> None:
        self.horloge = horloge if horloge is not None else Horloge()
        self.entrees: list[dict] = []

    @staticmethod
    def corps(t: float, texte: str) -> str:
        ...
        return json.dumps({"t": t, "texte": texte}, sort_keys=True, ensure_ascii=False)
```

**Ligne par ligne.**

- `GENESE` vaut 64 zéros, la longueur d'une empreinte SHA-256 écrite en hexadécimal (256 bits, 4 bits par caractère). La première entrée n'a pas de précédente : elle se chaîne à la genèse, ce qui évite un cas particulier dans `journaliser` comme dans `verifier`.
- Le constructeur reçoit l'horloge du monde (celle que l'approbateur fera avancer) ou en crée une neuve à 0 s. Le temps est **simulé** : aucune ligne n'appelle `time.time()`, et le journal donne la même sortie à chaque exécution.
- `entrees` est une liste publique : les tests la lisent, et la démo la falsifie volontairement pour montrer que la falsification se voit.
- `corps` est une méthode **statique** : elle ne lit aucun attribut, elle transforme `(t, texte)` en texte. `sort_keys=True` garantit un texte unique pour un même contenu (sans lui, l'ordre des clés dépendrait de l'ordre d'insertion) ; `ensure_ascii=False` garde « •••• » et les accents lisibles, au lieu de les remplacer par des séquences d'échappement Unicode de six caractères.

**Analogie Java.** `corps` est une méthode `static`, et `json.dumps(..., sort_keys=True)` correspond à un `ObjectMapper` configuré avec `ORDER_MAP_ENTRIES_BY_KEYS` : une sérialisation **canonique**, condition pour qu'un hachage soit reproductible. L'horloge injectée est l'équivalent d'un `java.time.Clock` passé au constructeur, que les tests remplacent par une horloge fixe.

## Écrire : masquer, puis chaîner

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`JournalAudit.journaliser(evenement)`** — On peut se figurer un maillon de chaîne forgé par un forgeron qui soude chaque anneau nouveau à celui de la veille, mais qui commence toujours par limer les inscriptions dangereuses. La méthode reçoit l'événement brut et le confie d'abord à `masquer`, si bien que le clair n'est ni stocké ni haché ; elle prend ensuite l'empreinte de la dernière entrée, ou `GENESE` si le journal est vide, calcule le SHA-256 en hexadécimal de cette empreinte suivie du corps de l'instant courant et du texte masqué, encodés en UTF-8, et ajoute l'entrée aux quatre champs `t`, `texte`, `precedent` et `hash`. Elle rend le texte masqué, par exemple « virement vers [IBAN ••••3456] », que l'appelant peut afficher sans crainte.

**`JournalAudit.textes()`** — Cette méthode est la liseuse qui ne regarde que l'encre des pages, jamais les sceaux. Elle ne reçoit rien d'autre que le journal lui-même, parcourt `self.entrees` dans l'ordre d'écriture et rend la liste de leurs seuls champs `texte`, tous déjà masqués. Elle ne modifie rien et ne lève aucune exception ; les tests et la démonstration s'en servent pour comparer ce qui a été écrit aux lignes attendues, et l'exemple de l'énoncé s'en sert pour passer la première entrée à `JournalAudit.corps`.

```python
# [extrait] agent/garde_fous.py
class JournalAudit:
    ...
    def journaliser(self, evenement: str) -> str:
        """Masque PUIS écrit (le journal ne voit jamais le clair) ; rend le texte masqué écrit."""
        texte = masquer(evenement)
        precedent = self.entrees[-1]["hash"] if self.entrees else GENESE
        h = hashlib.sha256((precedent + self.corps(self.horloge.t, texte)).encode("utf-8")).hexdigest()
        self.entrees.append({"t": self.horloge.t, "texte": texte, "precedent": precedent, "hash": h})
        return texte

    def textes(self) -> list[str]:
        """Les textes masqués, dans l'ordre d'écriture."""
        return [e["texte"] for e in self.entrees]
```

**Ligne par ligne.**

- `texte = masquer(evenement)` est la **première** ligne : à partir d'ici, la méthode ne manipule plus que le texte masqué. Le clair n'est ni stocké, ni haché.
- `precedent` est l'empreinte de la dernière entrée, ou la genèse si le journal est vide.
- `h` est le SHA-256 de la concaténation « empreinte précédente + corps ». `.encode("utf-8")` est obligatoire : `hashlib` hache des **octets**, pas des chaînes. `.hexdigest()` rend les 64 caractères hexadécimaux.
- L'entrée stocke `t` et `texte` (de quoi recalculer le corps), `precedent` et `hash` (de quoi vérifier le chaînage).
- La méthode rend le texte masqué : l'appelant peut l'afficher sans risque, et le test peut le comparer.

Pour l'exemple de l'énoncé, horloge à 5 s :

```text
>>> j = JournalAudit(Horloge(5.0))
>>> j.journaliser("virement vers AE07 0331 2345 6789 0123 456")
'virement vers [IBAN ••••3456]'
>>> JournalAudit.corps(5.0, j.textes()[0])
'{"t": 5.0, "texte": "virement vers [IBAN ••••3456]"}'
>>> j.entrees[0]["hash"]
'6ffa62ed999b2964d5f9b4b2f3cda79fab9ec647087fa1b9fafcb92600a556ae'
```

**Analogie Java.** `hashlib.sha256(octets).hexdigest()` s'écrit `HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(texte.getBytes(StandardCharsets.UTF_8)))`.

**Le piège classique.** Masquer **après** avoir haché, ou hacher le texte brut et stocker le texte masqué. Dans le premier cas, le clair a déjà circulé ; dans le second, la vérification ne pourra jamais recalculer l'empreinte, puisqu'elle n'a plus le texte qui a servi au calcul. Ce qu'on hache doit être exactement ce qu'on stocke.

## Vérifier : recalculer, ne jamais faire confiance

Un brouillon tentant ne regarde que le chaînage stocké :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`verifier(entrees)`** — Ce brouillon est un contrôleur de train qui vérifie que chaque wagon est bien accroché au précédent, sans jamais ouvrir les portes pour voir ce qu'il transporte. Il reçoit la liste des entrées, la parcourt à partir de l'indice 1 et rend le premier indice dont le champ `precedent` diffère du champ `hash` de l'entrée d'avant ; si tous les attelages concordent, il rend `None`. Comme il ne recalcule aucune empreinte, une entrée dont on a seulement réécrit le texte, « b » devenu « b modifié », garde des champs cohérents entre eux, et la falsification passe inaperçue.

```python
# [extrait] brouillon
def verifier(entrees):
    for i in range(1, len(entrees)):
        if entrees[i]["precedent"] != entrees[i - 1]["hash"]:
            return i
    return None
```

Il ne recalcule rien. Si l'on remplace le texte de l'entrée 1 par « b modifié », les champs `precedent` et `hash` n'ont pas bougé, ils sont toujours cohérents entre eux, et ce brouillon rend `None` : la falsification passe inaperçue. La bonne version recalcule chaque empreinte à partir du contenu :

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`JournalAudit.verifier()`** — Cette fois, le contrôleur ouvre chaque wagon et repèse lui-même la marchandise. La méthode ne reçoit rien d'autre que le journal ; elle part de la genèse, puis, pour chaque entrée, refait exactement le calcul de l'écriture, SHA-256 de l'empreinte précédente suivie du corps rebâti à partir du `t` et du `texte` stockés, et compare à la fois le champ `precedent` à l'empreinte qu'elle vient de valider et le champ `hash` au recalcul. À la première discordance, elle rend l'indice de l'entrée fautive, 1 dans le test où l'entrée 1 a été réécrite ; si la boucle va jusqu'au bout, elle rend `None`, signe que la chaîne est intacte.

```python
# [extrait] agent/garde_fous.py
class JournalAudit:
    ...
    def verifier(self) -> int | None:
        """Indice de la première entrée incohérente, None si toute la chaîne est intacte."""
        precedent = GENESE
        for i, e in enumerate(self.entrees):
            attendu = hashlib.sha256((precedent + self.corps(e["t"], e["texte"])).encode("utf-8")).hexdigest()
            if e["precedent"] != precedent or e["hash"] != attendu:
                return i
            precedent = e["hash"]
        return None
```

**Ligne par ligne.**

- On repart de la genèse, comme `journaliser` l'a fait pour la première entrée.
- Pour chaque entrée, `attendu` refait **exactement** le calcul de `journaliser`, avec le `t` et le `texte` stockés : c'est pourquoi `corps` a été isolé dans une méthode, partagée par les deux.
- Deux comparaisons : le champ `precedent` doit être l'empreinte qu'on vient de valider (sinon une entrée a été insérée, supprimée ou déplacée), et le `hash` doit être le recalcul (sinon le contenu a changé).
- `precedent = e["hash"]` avance d'un maillon. Si la boucle se termine, toute la chaîne est intacte : `None`, selon la convention du parcours pour « rien à signaler ».

**Pourquoi l'indice exact ?** Supposons les entrées 0 à i − 1 intactes et l'entrée i modifiée. Le recalcul utilise le corps modifié, dont l'empreinte diffère de celle stockée (sauf collision de SHA-256, négligeable) : la boucle s'arrête à i, ni avant ni après.

**La limite.** Un faussaire qui recalcule toutes les empreintes à partir de l'entrée modifiée rend la chaîne cohérente. La parade est l'**ancre** : publier régulièrement la dernière empreinte hors de sa portée (étape 66, point 7). C'est le premier défi bonus de l'énoncé.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestJournal
```

`test_masque_avant_d_ecrire_et_chaine` vérifie que le texte rendu est masqué, recalcule lui-même la première empreinte avec `GENESE` et `JournalAudit.corps(5.0, …)`, vérifie que la deuxième entrée pointe vers elle avec `t = 15.0` (5 s + 10 s), et que `verifier()` vaut `None`. `test_modification_detectee` modifie le texte de l'entrée 1 sur trois et attend 1.
