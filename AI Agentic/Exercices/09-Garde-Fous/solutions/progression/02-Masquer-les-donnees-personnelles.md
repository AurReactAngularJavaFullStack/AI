# Étape 2 — Masquer les données personnelles

> [Énoncé du palier 09](<../../README.md>) · Précédent : [Étape 1 — La politique de refus par défaut](<01-Politique-de-refus-par-defaut.md>) · Suivant : [Étape 3 — Le journal d'audit chaîné](<03-Journal-d-audit-chaine.md>)

## Comment raisonner

Le journal d'audit va tout enregistrer : les questions des clients, les décisions de la politique, les virements demandés. Si l'on y écrit un IBAN ou un numéro d'Emirates ID en clair, le journal devient une copie non maîtrisée de données personnelles, contraire au principe de minimisation de la PDPL. Il faut donc une fonction qui remplace ces données par une étiquette **avant** toute écriture, en gardant juste ce qu'il faut pour le travail : les quatre derniers chiffres.

On raisonne en deux temps. D'abord, **la liste des formats** que l'agent rencontre aux Émirats : e-mail, IBAN AE (23 caractères), Emirates ID (15 chiffres commençant par 784), téléphone +971 ou 05…, et un filet pour tout le reste. Ensuite, **l'ordre** des remplacements, qui est la vraie difficulté : chaque règle travaille sur le texte déjà transformé par les précédentes.

## Un brouillon, et ce qui ne va pas

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`masquer(texte_brut)`** — Ce brouillon fait penser à un employé zélé qui passe le gros rouleau de peinture sur le mur avant que le peintre de précision ait pu tracer ses lettres. Il reçoit le texte brut, remplace d'abord toute suite d'au moins neuf chiffres par l'étiquette `[NUMERO]`, puis cherche dans le résultat un IBAN AE suivi de 21 chiffres pour le remplacer par `[IBAN]`, et rend la chaîne obtenue. Comme le filet est passé le premier, l'IBAN n'existe déjà plus quand la seconde règle le cherche : « IBAN AE07 0331 2345 6789 0123 456 » ressort en « IBAN AE[NUMERO] », sans les quatre derniers chiffres, ce qui montre pourquoi l'ordre et la fin du numéro comptent.

```python
# [extrait] brouillon
def masquer(texte_brut):
    t = re.sub(r"\d(?:[ -]?\d){8,}", "[NUMERO]", texte_brut)       # le filet d'abord : erreur
    t = re.sub(r"\bAE\d{2}(?: ?\d){19}\b", "[IBAN]", t)
    return t
```

Sur « IBAN AE07 0331 2345 6789 0123 456 », ce brouillon rend « IBAN AE[NUMERO] » : le filet a avalé les 21 chiffres avant que la règle de l'IBAN ne les voie, et celle-ci ne trouve plus rien. Le texte est protégé, mais l'étiquette est fausse, et un auditeur ne sait plus qu'il s'agissait d'un IBAN. Deuxième défaut : aucune étiquette ne garde les quatre derniers chiffres, si bien qu'un conseiller ne peut plus dire au client « le compte se terminant par 3456 ». Règle : **du plus spécifique au plus général**, le filet en dernier.

## Les quatre derniers chiffres

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`masquer(texte_brut)`** — Dans cet extrait, la fonction principale ne montre encore que son atelier intérieur : elle reçoit le texte brut, et les points de suspension tiennent la place des cinq substitutions qui viendront dans les extraits suivants, pour finalement rendre le texte caviardé. Ce qui compte ici, c'est qu'elle abrite dans son propre corps un petit outil de découpe, défini une fois et réutilisé par chaque règle, si bien que toutes les étiquettes `[IBAN …]`, `[EMIRATES_ID …]`, `[TEL …]` ou `[NUMERO …]` finiront de la même manière, par les quatre derniers chiffres.

**`fin(m)`** — Cette fonction interne, qui vit dans `masquer`, est le relieur qui garde seulement le coin du ticket où figurent les derniers chiffres. Elle reçoit l'objet de correspondance `m` que `re.sub` lui tend, lit le passage entier `m.group(0)`, en extrait un à un les seuls caractères qui sont des chiffres, garde les quatre derniers et les fait précéder de quatre points noirs `••••`. Pour « +971 50 123 4567 », elle isole « 971501234567 » et rend « ••••4567 » ; elle ne lève aucune exception et ne sert qu'à composer la fin de chaque étiquette.

```python
# [extrait] agent/garde_fous.py
def masquer(texte_brut: str) -> str:
    ...
    def fin(m: re.Match) -> str:
        return "••••" + "".join(c for c in m.group(0) if c.isdigit())[-4:]
```

`m` est l'objet « correspondance » que `re.sub` passe à une fonction de remplacement ; `m.group(0)` est le passage reconnu en entier, par exemple « +971 50 123 4567 ». La compréhension garde ses seuls chiffres, « 971501234567 », et `[-4:]` prend les quatre derniers, « 4567 ». La fonction est définie **dans** `masquer` parce qu'elle ne sert qu'à elle : c'est l'équivalent d'une méthode privée, sans polluer l'espace de noms du module.

## E-mail et IBAN

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`masquer(texte_brut)`** — C'est la même fonction que dans l'extrait précédent, vue cette fois au moment où le greffier ouvre son dossier et commence par les données les plus faciles à reconnaître. Elle reçoit le texte brut, remplace d'abord toute adresse e-mail par `[EMAIL]`, puis repère chaque « AE » suivi de 21 chiffres, espaces facultatives comprises, et confie le passage à une petite fonction anonyme : si `iban_ae_valide` accepte la clé mod 97, le passage devient `[IBAN ••••3456]` grâce à `fin`, sinon il est rendu tel quel pour que le filet le reprenne plus loin. Le résultat intermédiaire `t` passe ensuite aux règles suivantes, que l'extrait laisse en pointillés.

```python
# [extrait] agent/garde_fous.py
def masquer(texte_brut: str) -> str:
    ...
    t = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[EMAIL]", texte_brut)
    t = re.sub(r"\bAE\d{2}(?: ?\d){19}\b",
               lambda m: f"[IBAN {fin(m)}]" if iban_ae_valide(m.group(0)) else m.group(0), t)
    ...
```

**L'e-mail.** `[\w.+-]+` est la partie locale (lettres, chiffres, point, plus, tiret), puis `@`, puis un nom de domaine `[\w-]+` suivi d'au moins un `.quelquechose`. On le traite en premier parce qu'une adresse peut contenir des chiffres (`c-1@banque-b1.ae`) qu'une règle numérique abîmerait.

**L'IBAN.** `\bAE` exige que « AE » commence un mot ; `\d{2}` est la clé de contrôle ; `(?: ?\d){19}` lit 19 chiffres, chacun précédé d'une espace facultative, ce qui accepte la forme compacte comme la forme groupée par quatre. Le remplacement n'est pas une chaîne fixe mais une **fonction** (`lambda m: …`) : si `iban_ae_valide` (palier 03) accepte le passage, on rend l'étiquette `[IBAN ••••3456]` ; sinon, on rend `m.group(0)`, c'est-à-dire le passage **inchangé**. Un IBAN à clé fausse n'est donc pas étiqueté IBAN, mais il n'est pas pour autant laissé en clair : le filet s'en chargera.

**Pourquoi un contrôle de clé pour masquer ?** Les contrôles mod 97 (et Luhn pour les cartes) servent à **nommer** correctement la donnée, pas à décider s'il faut la masquer (étape 66). Une suite de 21 chiffres qui ne passe aucun contrôle reste une suite de 21 chiffres, et elle sort sous l'étiquette générique.

**Analogie Java.** `re.sub(motif, fonction, texte)` est `Pattern.compile(motif).matcher(texte).replaceAll(m -> …)` (Java 9 et suivants), où la fonction reçoit un `MatchResult`.

## Emirates ID, téléphone et filet

**Ce que fait chaque fonction, avant d'entrer dans le code.**

**`masquer(texte_brut)`** — C'est toujours la même fonction, qui achève ici sa tournée comme un pêcheur relevant ses filets du plus fin au plus large. Après l'e-mail et l'IBAN, elle cherche un Emirates ID au format 784-AAAA-NNNNNNN-C et ne le change en `[EMIRATES_ID ••••dddd]` que si `emirates_id_format_valide` l'accepte, puis remplace sans contrôle tout numéro en +971, 00971 ou 05 par `[TEL ••••dddd]`. Elle rend enfin le texte après le dernier filet, qui étiquette `[NUMERO ••••dddd]` toute suite restante d'au moins neuf chiffres : un montant de six chiffres comme 180000 passe entre les mailles, tandis qu'un IBAN à clé fausse y reste pris.

```python
# [extrait] agent/garde_fous.py
def masquer(texte_brut: str) -> str:
    ...
    t = re.sub(r"\b784[- ]?\d{4}[- ]?\d{7}[- ]?\d\b",
               lambda m: f"[EMIRATES_ID {fin(m)}]" if emirates_id_format_valide(m.group(0)) else m.group(0), t)
    t = re.sub(r"(?:\+|\b00)971[ -]?\d(?:[ -]?\d){7,8}\b|\b05\d(?:[ -]?\d){7}\b", lambda m: f"[TEL {fin(m)}]", t)
    return re.sub(r"\d(?:[ -]?\d){8,}", lambda m: f"[NUMERO {fin(m)}]", t)
```

**L'Emirates ID.** Le motif suit l'affichage officiel 784-AAAA-NNNNNNN-C : `784`, quatre chiffres (l'année), sept chiffres, un chiffre de contrôle, chaque groupe séparé par un tiret ou une espace facultatifs. `emirates_id_format_valide` (palier 03) revérifie les 15 chiffres ; comme pour l'IBAN, un échec laisse le passage au filet.

**Le téléphone.** Deux alternatives séparées par `|`. La première : `+971` ou `00971`, puis 8 ou 9 chiffres avec séparateurs facultatifs (un premier chiffre, puis 7 ou 8 répétitions du groupe), ce qui couvre un fixe et un mobile. On n'écrit pas `\b` devant le `+`, parce que `\b` exige une lettre ou un chiffre d'un côté, et qu'une espace suivie de `+` n'en a aucun ; on l'écrit devant `00`, pour ne pas couper un numéro plus long. La seconde : un mobile local `05X` suivi de 7 chiffres. Ici, pas de contrôle : tout ce qui a la forme d'un téléphone est masqué.

**Le filet.** `\d(?:[ -]?\d){8,}` : un chiffre, puis au moins huit autres, chacun précédé d'une espace ou d'un tiret facultatifs. Au moins neuf chiffres, donc. Un montant comme 180000 (six chiffres) reste lisible, et c'est voulu : le journal doit dire combien a été demandé.

**Le piège classique.** Oublier le `r` devant les motifs. Dans `"\bAE"`, sans `r`, Python lit `\b` comme le caractère « retour arrière » (code 8), et le motif ne correspond plus jamais : `re.sub("\bAE", "X", "AE07")` rend « AE07 » inchangé, sans aucune erreur. Avec `r"\bAE"`, `\b` arrive intact au moteur d'expressions régulières, qui le lit comme une frontière de mot. En Java, le même piège existe sous une autre forme : il faut doubler la barre, `"\\bAE"`.

## Les tests qui passent maintenant

Depuis `projet/` :

```text
python -m unittest -v tests.test_09_garde_fous.TestMasquage
```

`test_identite_et_telephone` vérifie le cas de l'énoncé : les chiffres de « 784-1990-1234567-1 » finissent par 5671, ceux de « +971 50 123 4567 » par 4567. `test_iban_email_et_long_numero` vérifie l'IBAN valide (`[IBAN ••••3456]`), l'adresse `c-1@banque-b1.ae` (`[EMAIL]`), l'IBAN à clé 08 qui finit dans le filet (« AE[NUMERO ••••3456] » : les lettres restent, les chiffres disparaissent) et le montant de six chiffres, laissé en clair.
